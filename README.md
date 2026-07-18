
---

## ⚙️ Hardware Architecture

| **Component**         | **Description**                               |
|-----------------------|-----------------------------------------------|
| **SLG47910V FPGA**    | iCE40 UltraPlus, ~1,120 LUTs                  |
| **RP2040**            | Dual‑core ARM Cortex‑M0+ @ 133 MHz            |
| **HC‑SR04**           | Ultrasonic distance sensor (2–400 cm)         |
| **Onboard LED**       | Time‑multiplexed 8‑bit pattern display        |

### FPGA Internal Modules

| **Module**             | **Function**                             | **LUTs** |
|------------------------|------------------------------------------|----------|
| SPI_TARGET             | SPI slave interface                      | ~28      |
| SPI Decoder            | 2‑byte instruction parser                | ~14      |
| CPU_CORE               | 8‑bit processor with 16 instructions     | ~45      |
| ALU_8BIT               | Arithmetic & logic operations            | ~35      |
| ULTRASONIC_SENSOR      | HC‑SR04 interface with debounce          | ~42      |
| LED Sequencer          | Time‑multiplexed LED driver              | ~18      |

**Total utilisation:** 374 LUTs (~33% of available 1,120 LUTs)

---

## 🔌 Pin Mapping & Port Assignments (FPGA)

The following table defines the physical pin mapping for the **SLG47910V** FPGA:

| **Function Name**   | **Direction** | **Signal**              | **Port Assign** |
|---------------------|---------------|-------------------------|-----------------|
| GPIO18_IN           | Input         | rst_n                   | PIN 9           |
| GPIO16_OUT          | Output        | led16                   | PIN 7           |
| GPIO16_OE           | Output        | led16_en                | PIN 7           |
| GPIO6_OUT           | Output        | spi_miso                | PIN 19          |
| GPIO6_OE            | Output        | spi_miso_en             | PIN 19          |
| GPIO3_IN            | Input         | spi_sck                 | PIN 16          |
| GPIO2_OUT           | Output        | object_detected_pin     | PIN 15          |
| GPIO2_OE            | Output        | object_detected_en      | PIN 15          |
| GPIO5_IN            | Input         | spi_mosi                | PIN 18          |
| GPIO4_IN            | Input         | spi_ss_n                | PIN 17          |
| GPIO1_OUT           | Output        | trig                    | PIN 14          |
| GPIO1_OE            | Output        | trig_en                 | PIN 14          |
| GPIO0_IN            | Input         | echo                    | PIN 13          |
| OSC_EN              | Output        | clk_en                  | —               |
| OSC_CLK             | Input         | clk                     | —               |

### Signal Description

| **Signal**             | **Direction** | **Description**                            |
|------------------------|---------------|--------------------------------------------|
| **clk**                | Input         | 50 MHz system clock                        |
| **clk_en**             | Output        | Clock enable (always HIGH)                 |
| **rst_n**              | Input         | Active‑LOW reset                           |
| **spi_ss_n**           | Input         | SPI Slave Select (Active LOW)              |
| **spi_sck**            | Input         | SPI Clock from RP2040                      |
| **spi_mosi**           | Input         | SPI Data In (RP2040 → FPGA)                |
| **spi_miso**           | Output        | SPI Data Out (FPGA → RP2040)               |
| **spi_miso_en**        | Output        | MISO output enable                         |
| **echo**               | Input         | HC‑SR04 Echo input                         |
| **trig**               | Output        | HC‑SR04 Trigger output                     |
| **trig_en**            | Output        | Trigger output enable                      |
| **led16**              | Output        | Onboard LED display                        |
| **led16_en**           | Output        | LED output enable                          |
| **object_detected_pin**| Output        | Direct sensor status                       |
| **object_detected_en** | Output        | Sensor status output enable                |

---

## 🔄 SPI Communication

**Protocol:** Mode 0 (CPOL=0, CPHA=0)  
**Clock:** 50 kHz  
**Data Format:** MSB‑first, 8‑bit transfers, full‑duplex  

**2‑Byte Instruction Format:**

| **Byte**          | **Bit7** | **Bit6** | **Bit5** | **Bit4** | **Bit3** | **Bit2** | **Bit1** | **Bit0** |
|-------------------|----------|----------|----------|----------|----------|----------|----------|----------|
| Byte 1 (Opcode)   | 0        | 0        | 0        | op[4]    | op[3]    | op[2]    | op[1]    | op[0]    |
| Byte 2 (Data)     | d[7]     | d[6]     | d[5]     | d[4]     | d[3]     | d[2]     | d[1]     | d[0]     |

---

## 💻 Instruction Set

| **Mnemonic** | **Opcode (hex)** | **Operand** | **Description**                   |
|--------------|------------------|-------------|-----------------------------------|
| LDA          | 0x01             | 8‑bit       | Load immediate                    |
| ADD          | 0x02             | 8‑bit       | Add                               |
| SUB          | 0x03             | 8‑bit       | Subtract                          |
| AND          | 0x04             | 8‑bit       | Bitwise AND                       |
| OR           | 0x05             | 8‑bit       | Bitwise OR                        |
| XOR          | 0x06             | 8‑bit       | Bitwise XOR                       |
| LSL          | 0x07             | none        | Logical shift left                |
| LSR          | 0x08             | none        | Logical shift right               |
| ROL          | 0x09             | none        | Rotate left                       |
| ROR          | 0x0A             | none        | Rotate right                      |
| INC          | 0x0B             | none        | Increment                         |
| DEC          | 0x0C             | none        | Decrement                         |
| JMP          | 0x0D             | 8‑bit       | Unconditional jump                |
| JZ           | 0x0E             | 8‑bit       | Jump if zero                      |
| JNZ          | 0x0F             | 8‑bit       | Jump if not zero                  |
| SENSE        | 0x10             | none        | Read ultrasonic sensor            |
| OUT          | 0x12             | 8‑bit       | Output to LED port                |

**Special terminal command:** `OUTA` – outputs the current accumulator value to the LED.

---

## 📊 Resource Utilization (FPGA)

| **Resource**               | **Used** | **Available** | **Utilisation** |
|----------------------------|----------|---------------|-----------------|
| CLB LUTs                   | 374      | (device)      | ~33%            |
| Flip‑Flops (FFs)           | 188      | —             | —               |
| CLB Function Generators    | 183      | —             | —               |
| Input/Output Buffers       | 5        | 120           | 4%              |
| Clock Buffers              | 70       | 130           | 54%             |
| RTL Output Ports           | 9        | —             | —               |
| RTL Input Ports            | 6        | —             | —               |
| GPIO Used                  | 9        | 19            | 47%             |
| Oscillators                | 1        | —             | —               |
| 4KB BRAM                   | 0        | 8             | 0%              |

---

## 🚀 Getting Started

### 1. Hardware Setup
- **Shrike Light Board** (SLG47910V FPGA + RP2040)
- **HC‑SR04** ultrasonic sensor (connect via external wires)
- **USB Type‑C** cable for programming

### 2. Software Requirements
- **Go Configure Software Hub** (FPGA programming)
- **MicroPython IDE (Thonny)** (RP2040 terminal)
- **Yosys + nextpnr + IceStorm** (open‑source synthesis)

### 3. Flash the FPGA
```bash
# Synthesize
yosys -p "read_verilog src/*.v; synth_ice40 -top top -json nova8.json"

# Place & route
nextpnr-ice40 --up5k --package sg48 --pcf nova8.pcf --json nova8.json --asc nova8.asc

# Generate bitstream
icepack nova8.asc nova8.bin
