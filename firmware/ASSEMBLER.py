from machine import Pin, SPI
import time

# Pins
SCK, CS, MOSI, MISO, RST = 2, 1, 3, 0, 14

# Opcodes
OP_NOP = 0x00
OP_LDA = 0x01
OP_ADD = 0x02
OP_SUB = 0x03
OP_AND = 0x04
OP_OR  = 0x05
OP_XOR = 0x06
OP_LSL = 0x07
OP_LSR = 0x08
OP_INC = 0x0B
OP_DEC = 0x0C
OP_READ_SENSOR = 0x10
OP_MOV_PORT16  = 0x12

# Instruction map
INSTR = {
    "lda": (OP_LDA, True), "add": (OP_ADD, True), "sub": (OP_SUB, True),
    "and": (OP_AND, True), "or":  (OP_OR,  True), "xor": (OP_XOR, True),
    "inc": (OP_INC, False), "dec": (OP_DEC, False),
    "lsl": (OP_LSL, False), "lsr": (OP_LSR, False),
    "sense": (OP_READ_SENSOR, False),
    "out": (OP_MOV_PORT16, True),
}

# Init SPI
rst = Pin(RST, Pin.OUT, value=1)
cs = Pin(CS, Pin.OUT, value=1)
spi = SPI(0, baudrate=50_000, polarity=0, phase=0, bits=8,
          sck=Pin(SCK), mosi=Pin(MOSI), miso=Pin(MISO))

def reset_fpga():
    rst.value(0); time.sleep_ms(200)
    rst.value(1); time.sleep_ms(300)

def send(opcode, data):
    cs.value(0)
    spi.write(bytes([opcode & 0x1F, data & 0xFF]))
    cs.value(1); time.sleep_ms(20)
    rx = bytearray(2)
    cs.value(0)
    spi.write_readinto(bytes([OP_NOP, 0x00]), rx)
    cs.value(1)
    return rx[1]

def parse_val(s):
    s = s.strip().lower()
    if s.startswith("0x"): return int(s, 16)
    if s.startswith("0b"): return int(s, 2)
    return int(s)

def parse_line(line):
    line = line.strip()
    if not line or line.startswith(";") or line.startswith("#"):
        return None
    parts = line.split()
    mnem = parts[0].lower()
    if mnem == "outa":
        return ("outa", 0)
    if mnem == "delay":
        if len(parts) < 2: return ("error", "DELAY needs value")
        return ("delay", parse_val(parts[1]))
    if mnem not in INSTR:
        return ("error", f"Unknown: {mnem}")
    opcode, needs_data = INSTR[mnem]
    if needs_data:
        if len(parts) < 2: return ("error", f"{mnem.upper()} needs value")
        return (opcode, parse_val(parts[1]))
    return (opcode, 0)

def exec_line(parsed, acc):
    """Execute one parsed line. Returns (new_acc, description)"""
    opcode, data = parsed
    if opcode == "outa":
        send(OP_MOV_PORT16, acc)
        return (acc, f"OUTA      -> LED = 0x{acc:02X}")
    elif opcode == "delay":
        time.sleep_ms(data)
        return (acc, f"DELAY {data}ms")
    elif opcode == "error":
        return (acc, f"ERROR: {data}")
    else:
        new_acc = send(opcode, data)
        mnem = {v[0]:k for k,v in INSTR.items()}.get(opcode, "???")
        if mnem in ("lda","add","sub","and","or","xor"):
            return (new_acc, f"{mnem.upper():4s} {data:3d}  -> Acc = {new_acc}")
        elif mnem == "sense":
            status = "DETECTED" if new_acc else "CLEAR"
            return (new_acc, f"SENSE     -> Acc = {new_acc} ({status})")
        elif mnem == "out":
            return (new_acc, f"OUT  {data:3d}  -> LED = 0x{data:02X}")
        else:
            return (new_acc, f"{mnem.upper():4s}       -> Acc = {new_acc}")

def execute_buffer(buffer, loop_mode=False):
    """Execute all lines in buffer. If loop_mode, repeats until Ctrl+C."""
    print("\n" + "-" * 45)
    print("  EXECUTING" + (" IN LOOP (Ctrl+C to stop)" if loop_mode else ""))
    print("-" * 45)

    try:
        while True:
            acc = 0
            for ln, raw, parsed in buffer:
                if parsed is None:
                    continue
                acc, desc = exec_line(parsed, acc)
                print(f"  [{ln:2d}] {desc}")

            if not loop_mode:
                break
            print("  --- loop restart ---")
            time.sleep_ms(100)

    except KeyboardInterrupt:
        print("\n  [BREAK] Loop stopped by user.")

    send(OP_MOV_PORT16, 0x00)  # Turn off LED
    print("-" * 45)
    print(f"  DONE. Final Acc = {acc}")
    print("-" * 45)

def print_help():
    print("""
┌─────────────────────────────────────────────┐
│  ASSEMBLY TERMINAL - QUICK REFERENCE        │
├─────────────────────────────────────────────┤
│  LDA <val>    Load value to Acc             │
│  ADD <val>    Add to Acc                    │
│  SUB <val>    Subtract from Acc             │
│  AND <val>    Bitwise AND                   │
│  OR  <val>    Bitwise OR                    │
│  XOR <val>    Bitwise XOR                   │
│  INC          Acc + 1                       │
│  DEC          Acc - 1                       │
│  LSL          Shift left                    │
│  LSR          Shift right                   │
│  OUT <val>    LED = value (0x00-0xFF)       │
│  OUTA         LED = Acc value               │
│  SENSE        Read sensor -> Acc            │
│  DELAY <ms>   Wait milliseconds             │
├─────────────────────────────────────────────┤
│  execute      Run code once                 │
│  loop         Run code in continuous loop   │
│  clear        Clear buffer                  │
│  list         Show current code             │
│  help         Show this help                │
│  quit         Exit                          │
└─────────────────────────────────────────────┘
""")

# ─── MAIN ───
print("=" * 50)
print("  VECTOR8_CPU ASSEMBLY TERMINAL")
print("=" * 50)
print("  Type 'help' for commands. 'execute' to run code.")
print("=" * 50)

reset_fpga()
buffer = []
line_num = 1

while True:
    try:
        cmd = input(f"\n[{line_num:2d}]> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
        send(OP_MOV_PORT16, 0x00)
        break

    if not cmd:
        continue

    low = cmd.lower()

    if low in ("quit", "q", "exit"):
        send(OP_MOV_PORT16, 0x00)
        print("Goodbye!")
        break

    elif low == "help" or low == "h":
        print_help()
        continue

    elif low == "clear":
        buffer = []
        line_num = 1
        print("  [CLEARED] Buffer empty.")
        continue

    elif low == "list":
        if not buffer:
            print("  [EMPTY] No code.")
        else:
            for ln, raw, _ in buffer:
                print(f"    {ln:2d}: {raw}")
        continue

    elif low == "execute" or low == "run" or low == "exec":
        execute_buffer(buffer, loop_mode=False)
        continue

    elif low == "loop":
        execute_buffer(buffer, loop_mode=True)
        continue

    # Parse as assembly instruction
    parsed = parse_line(cmd)
    if parsed and parsed[0] == "error":
        print(f"  [ERROR] {parsed[1]}")
    else:
        buffer.append((line_num, cmd, parsed))
        print(f"  [OK] Line {line_num}")
        line_num += 1