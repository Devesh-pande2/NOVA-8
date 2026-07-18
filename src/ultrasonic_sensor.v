module ultrasonic_sensor #(
    parameter CLK_FREQ      = 50000000,
    parameter TRIG_PULSE_US = 10,
    parameter MAX_DIST_CM   = 20
) (
    input       clk,
    input       echo,
    output reg  trig,
    output reg  object_detected
);
    // Integer-safe timing math (avoids float localparam risk)
    localparam MAX_ECHO_TIME_US = (MAX_DIST_CM * 1000 * 1000) / 17150;
    localparam MAX_COUNT        = (MAX_ECHO_TIME_US * (CLK_FREQ / 1000000));
    localparam DEBOUNCE_CNT_LIMIT = 500000;

    reg [31:0]  echo_count = 0;
    reg         echo_prev = 0;
    reg [31:0]  trig_counter = 0;
    reg         detect = 0;
    reg [31:0]  debounce_clk_cnt = 0;

    // Trigger pulse generator (10us pulse every 60ms)
    always @(posedge clk) begin
        if (trig_counter < (CLK_FREQ * 60_000 / 1_000_000))
            trig_counter <= trig_counter + 1;
        else
            trig_counter <= 0;

        if (trig_counter < (TRIG_PULSE_US * (CLK_FREQ / 1_000_000)))
            trig <= 1;
        else
            trig <= 0;
    end

    // Echo pulse measurement
    always @(posedge clk) begin
        echo_prev <= echo;
        if (~echo_prev && echo)
            echo_count <= 0;
        else if (echo)
            echo_count <= echo_count + 1;

        if (echo_prev && ~echo) begin
            if (echo_count <= MAX_COUNT)
                detect <= 1;
            else
                detect <= 0;
        end
    end

    // Debounce logic
    always @(posedge clk) begin
        if ((object_detected != detect) && (debounce_clk_cnt < DEBOUNCE_CNT_LIMIT)) begin
            debounce_clk_cnt <= debounce_clk_cnt + 1;
        end else if (debounce_clk_cnt == DEBOUNCE_CNT_LIMIT) begin
            object_detected <= detect;
            debounce_clk_cnt <= 0;
        end else begin
            debounce_clk_cnt <= 0;
        end
    end
endmodule