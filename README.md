# NOVA-8 – Custom 8‑Bit RISC Processor on SLG47910V FPGA

[![FPGA](https://img.shields.io/badge/FPGA-iCE40%20UltraPlus-blue)](https://www.latticesemi.com/)
[![Verilog](https://img.shields.io/badge/HDL-Verilog-forestgreen)](https://en.wikipedia.org/wiki/Verilog)
[![MicroPython](https://img.shields.io/badge/MicroPython-RP2040-yellow)](https://micropython.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## 📌 Project Overview

**NOVA-8** is a fully custom 8‑bit single‑cycle RISC processor implemented on the **SLG47910V** FPGA (iCE40 UltraPlus family). It features a Harvard architecture with 16 instructions, an SPI slave interface for real‑time instruction loading, an HC‑SR04 ultrasonic sensor interface, and a time‑multiplexed LED display.

The processor is controlled by an onboard **RP2040** microcontroller running a MicroPython assembly terminal, providing an interactive programming environment over the internal SPI bus.

---

## 📁 Repository Structure
NOVA-8/
├── README.md # This file
├── src/ # Verilog source files
│ ├── top.v # Top‑level module
│ ├── spi_target.v # SPI slave interface
│ ├── cpu_core.v # 8‑bit CPU core
│ ├── alu_8bit.v # Arithmetic Logic Unit
│ └── ultrasonic_sensor.v # HC‑SR04 sensor driver
├── bitstream/ # Pre‑generated bitstream files
│ └── nova8.bin # Ready‑to‑flash bitstream
├── firmware/ # RP2040 MicroPython code
│ ├── asm_terminal.py # Assembly terminal
│ └── main.py # FPGA flashing script
├── docs/ # Documentation
│ ├── ACIIS_Structure.pdf # System block diagrams & architecture
│ ├── Explanation.pdf # Line‑by‑line code explanation
│ ├── NOVA-8_Report.pdf # Full technical report
│ └── images/ # Screenshots and diagrams
└── video/ # Demonstration video
└── NOVA-8_Demo.mp4

text

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

### Hardware Setup
- **Shrike Light Board** (SLG47910V FPGA + RP2040)
- **HC‑SR04** ultrasonic sensor (connect via external wires)
- **USB Type‑C** cable for programming

### Software Requirements
- **Go Configure Software Hub** – for FPGA synthesis and bitstream generation
- **MicroPython IDE (Thonny)** – for running the assembly terminal on RP2040

---

### Method 1: Generate Bitstream from Source (Full Synthesis)

1. **Open Go Configure Software Hub** and create a new project.
2. **Add the Verilog source files** from the `src/` folder:
   - `top.v`
   - `spi_target.v`
   - `cpu_core.v`
   - `alu_8bit.v`
   - `ultrasonic_sensor.v`
3. **Assign the correct signal names** to the proper function names as per the pin mapping table above.
4. **Synthesize** the design and generate the bitstream.
5. The bitstream file (`nova8.bin`) will be created in the **bitstream folder**.
6. **Copy the bitstream file** to your project folder or use it directly.

---

### Method 2: Use Pre‑generated Bitstream (Quick Start)

If you want to skip synthesis, a pre‑generated bitstream is available in the `bitstream/` folder:
bitstream/nova8.bin

text

You can directly flash this file to the FPGA using the method below.

---

### Flashing the FPGA (Both Methods)

1. **Connect the Shrike Light board** to your PC via USB Type‑C.

2. **Create a `main.py` file** with the following code:

```python
import shrike

# Flash the bitstream to the FPGA
shrike.flash("nova8.bin")
Note: Make sure the nova8.bin file is in the same directory as main.py, or provide the full path.

Run main.py – the bitstream will be flashed to the FPGA.

The FPGA is now programmed with the NOVA-8 processor.

Running the Assembly Terminal
Open Thonny IDE and connect to the RP2040.

Upload and run firmware/asm_terminal.py.

Type assembly instructions in the terminal:

text
> LDA 10
[OK] Line 1
> ADD 20
[OK] Line 2
> OUTA
[OK] Line 3
> execute
The terminal will display the accumulator value after each instruction.

Example Program
text
LDA 10
ADD 20
OUTA
Expected Output: LED displays binary pattern 0x1E (30)

📚 Documentation
Three comprehensive PDFs are provided in the docs/ folder:

Document	Description
ACIIS_Structure.pdf	Complete system block diagrams and architectural flow
Explanation.pdf	Line‑by‑line explanation of every Verilog module and Python code
NOVA-8_Report.pdf	Full technical report with literature review, methodology, results
📄 View ACIIS Structure
📄 View Code Explanation
📄 View Full Report

🎥 Demonstration Video
A complete walkthrough of the project is available:

📁 Download video

▶️ Watch on YouTube (update with your actual URL)

🔧 Future Improvements
Extended instruction set (MUL, DIV)

Stored‑program architecture using BRAM

UART interface for direct PC communication

PWM output for motor control

Interrupt support

2‑stage pipelining

Debugging interface with register readback

📝 License
This project is licensed under the MIT License – see the LICENSE file for details.

👨‍💻 Designed by
Devesh Pande
Independent Researcher & FPGA Enthusiast

GitHub: @Devesh-pande2

LinkedIn: linkedin.com/in/your-profile

Email: your-email@example.com

🙏 Acknowledgments
Lattice Semiconductor – iCE40 FPGA family

Raspberry Pi Foundation – RP2040 microcontroller

Vocheric – Shrike Light board

⭐ Support
If you find this project useful, please consider giving it a star ⭐ on GitHub and sharing it with others!

Happy Building! 🚀

text

---

## 📋 Summary of Changes

| **Section** | **What Was Changed** |
|-------------|----------------------|
| **Repository Structure** | Added `bitstream/` folder for pre‑generated bitstream files |
| **Software Requirements** | Removed Yosys/nextpnr/IceStorm, kept only Go Configure and Thonny |
| **Flashing the FPGA** | Added `main.py` with `shrike.flash()` method |
| **Method 1** | Full synthesis workflow using Go Configure Software Hub |
| **Method 2** | Quick start using pre‑generated bitstream from `bitstream/` folder |
| **Flashing Instructions** | Clear steps: create `main.py` → import shrike → flash bitstream |

Copy this entire content into your `README.md` file on GitHub! 🎉
So I have not given mean dot PY we have to mention it in the read me and create a proper one text file this is broken because there are different different blocks that I have to copy and paste there so give me a proper readme file I can directly paste that code there and the file will be created inside readme .md
OK, the user is looking at the history of our conversation about the NOVA-8 FPGA project. They've been working on this for a while, and we've gone through multiple iterations of the report, the GitHub README, and the folder structure. The last thing they said is that the previous README I gave them was "broken because there are different different blocks that I have to copy and paste there." They want a single, complete code block they can directly copy and paste into their README.md file on GitHub.

So, the user's immediate need is a fully formatted, single-block Markdown file. They don't want to piece together sections. The deep need here is efficiency and avoiding errors. They're likely not a Markdown expert; they might be using the GitHub web interface and just want to paste one thing and be done. They also seem to be preparing this repository for public consumption (LinkedIn, showcasing skills), so a polished, complete README is crucial for first impressions.

Looking at the history, the user has been very specific about what should and shouldn't be in the README. They corrected me about the software tools (remove Yosys, use Go Configure). They specified the two methods for flashing the FPGA. They provided the exact pin mapping data. They also have three PDF documents (ACIIS Structure, Explanation, NOVA-8 Report) that they want prominently linked.

My response needs to deliver a single, self-contained Markdown block. It should include all the sections we've discussed: Overview, Repository Structure, Hardware Architecture, Pin Mapping, SPI Protocol, Instruction Set, Resource Utilization, Getting Started (with both methods), Documentation links, Future Improvements, License, and Author info. The user's name and GitHub link are already known from the history. I should also include the bitstream folder in the structure and mention the main.py script they haven't provided yet, but I can outline the steps for flashing.

I need to make the README visually clean and professional for LinkedIn and GitHub. Using badges, emojis, and clear tables will help. The tone should be enthusiastic and clear, suitable for a project showcase. I'll also remind them to replace placeholder links (YouTube, email, license) and to actually create the main.py file if they haven't already.

Alright, I'll structure the response by first providing the complete, single-code-block README. Then, I'll add a concise summary of what's included and what they need to do next (placeholders, creating main.py). That should cover their need for a "proper readme file I can directly paste."

Here is the complete, single README.md file that you can directly copy and paste into your GitHub repository. Everything is in one block – no separate sections to piece together.

markdown
# NOVA-8 – Custom 8‑Bit RISC Processor on SLG47910V FPGA

[![FPGA](https://img.shields.io/badge/FPGA-iCE40%20UltraPlus-blue)](https://www.latticesemi.com/)
[![Verilog](https://img.shields.io/badge/HDL-Verilog-forestgreen)](https://en.wikipedia.org/wiki/Verilog)
[![MicroPython](https://img.shields.io/badge/MicroPython-RP2040-yellow)](https://micropython.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## 📌 Project Overview

**NOVA-8** is a fully custom 8‑bit single‑cycle RISC processor implemented on the **SLG47910V** FPGA (iCE40 UltraPlus family). It features a Harvard architecture with 16 instructions, an SPI slave interface for real‑time instruction loading, an HC‑SR04 ultrasonic sensor interface, and a time‑multiplexed LED display.

The processor is controlled by an onboard **RP2040** microcontroller running a MicroPython assembly terminal, providing an interactive programming environment over the internal SPI bus.

---

## 📁 Repository Structure
NOVA-8/
├── README.md # This file
├── src/ # Verilog source files
│ ├── top.v # Top‑level module
│ ├── spi_target.v # SPI slave interface
│ ├── cpu_core.v # 8‑bit CPU core
│ ├── alu_8bit.v # Arithmetic Logic Unit
│ └── ultrasonic_sensor.v # HC‑SR04 sensor driver
├── bitstream/ # Pre‑generated bitstream files
│ └── nova8.bin # Ready‑to‑flash bitstream
├── firmware/ # RP2040 MicroPython code
│ ├── asm_terminal.py # Assembly terminal
│ └── main.py # FPGA flashing script
├── docs/ # Documentation
│ ├── ACIIS_Structure.pdf # System block diagrams & architecture
│ ├── Explanation.pdf # Line‑by‑line code explanation
│ ├── NOVA-8_Report.pdf # Full technical report
│ └── images/ # Screenshots and diagrams
└── video/ # Demonstration video
└── NOVA-8_Demo.mp4

text

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

### Hardware Setup
- **Shrike Light Board** (SLG47910V FPGA + RP2040)
- **HC‑SR04** ultrasonic sensor (connect via external wires)
- **USB Type‑C** cable for programming

### Software Requirements
- **Go Configure Software Hub** – for FPGA synthesis and bitstream generation
- **MicroPython IDE (Thonny)** – for running the assembly terminal on RP2040

---

### Method 1: Generate Bitstream from Source (Full Synthesis)

1. Open **Go Configure Software Hub** and create a new project.
2. Add the Verilog source files from the `src/` folder:
   - `top.v`
   - `spi_target.v`
   - `cpu_core.v`
   - `alu_8bit.v`
   - `ultrasonic_sensor.v`
3. Assign the correct signal names to the proper function names as per the pin mapping table above.
4. Synthesize the design and generate the bitstream.
5. The bitstream file (`nova8.bin`) will be created in the **bitstream folder**.
6. Copy the bitstream file to your project folder or use it directly.

---

### Method 2: Use Pre‑generated Bitstream (Quick Start)

If you want to skip synthesis, a pre‑generated bitstream is available in the `bitstream/` folder:
bitstream/nova8.bin

text

You can directly flash this file to the FPGA using the method below.

---

### Flashing the FPGA (Both Methods)

1. Connect the Shrike Light board to your PC via USB Type‑C.

2. Create a `main.py` file with the following code:

```python
import shrike

# Flash the bitstream to the FPGA
shrike.flash("nova8.bin")
Note: Make sure the nova8.bin file is in the same directory as main.py, or provide the full path.

Run main.py – the bitstream will be flashed to the FPGA.

The FPGA is now programmed with the NOVA-8 processor.

Running the Assembly Terminal
Open Thonny IDE and connect to the RP2040.

Upload and run firmware/asm_terminal.py.

Type assembly instructions in the terminal:

text
> LDA 10
[OK] Line 1
> ADD 20
[OK] Line 2
> OUTA
[OK] Line 3
> execute
The terminal will display the accumulator value after each instruction.

Example Program
text
LDA 10
ADD 20
OUTA
Expected Output: LED displays binary pattern 0x1E (30)

📚 Documentation
Three comprehensive PDFs are provided in the docs/ folder:

Document	Description
ACIIS_Structure.pdf	Complete system block diagrams and architectural flow
Explanation.pdf	Line‑by‑line explanation of every Verilog module and Python code
NOVA-8_Report.pdf	Full technical report with literature review, methodology, results
📄 View ACIIS Structure
📄 View Code Explanation
📄 View Full Report

🎥 Demonstration Video
A complete walkthrough of the project is available:

📁 Download video

▶️ Watch on YouTube

🔧 Future Improvements
Extended instruction set (MUL, DIV)

Stored‑program architecture using BRAM

UART interface for direct PC communication

PWM output for motor control

Interrupt support

2‑stage pipelining

Debugging interface with register readback

📝 License
This project is licensed under the MIT License – see the LICENSE file for details.

👨‍💻 Designed by
Devesh Pande
Independent Researcher & FPGA Enthusiast

GitHub: @Devesh-pande2

LinkedIn: linkedin.com/in/your-profile

Email: your-email@example.com

🙏 Acknowledgments
Lattice Semiconductor – iCE40 FPGA family

Raspberry Pi Foundation – RP2040 microcontroller

Vocheric – Shrike Light board

⭐ Support
If you find this project useful, please consider giving it a star ⭐ on GitHub and sharing it with others!

Happy Building! 🚀

text

---

## 📋 What to Do Next

| **Step** | **Action** |
|----------|------------|
| 1 | Go to `https://github.com/Devesh-pande2/NOVA-8` |
| 2 | Click **"Add file"** → **"Create new file"** |
| 3 | Name the file `README.md` |
| 4 | Copy the entire content above and paste it |
| 5 | Scroll down and click **"Commit new file"** |

---

## 🔗 Files You Need to Create

| **File** | **Location** | **Purpose** |
|----------|--------------|-------------|
| `main.py` | `firmware/main.py` | Flash bitstream using `shrike.flash()` |
| `asm_terminal.py` | `firmware/asm_terminal.py` | Assembly terminal for programming |
| `nova8.bin` | `bitstream/nova8.bin` | Pre‑generated bitstream |

---

## ⚠️ Important Notes

- Replace the placeholder YouTube link with your actual video URL.
- Replace the placeholder email and LinkedIn link with your actual details.
- If you don't have a `LICENSE` file yet, create one later (or remove the license badge).

Your README is now complete and ready to go! 🎉
