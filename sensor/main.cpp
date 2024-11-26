
#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>
#include <SPI.h>
#include <SoftwareSerial.h>
#include <Wire.h>

#define US_RX 13             // Ultrasonik RX pin
#define US_TX 12             // Ultrasonik TX pin
#define US_Baud 9600         // Ultrasonik Serial Baudrate
#define Depth_threshold 500  // Pasang/Surut in (mm)
#define GPIO_pulse 14        // Anemometer data pin
#define Serial_Lora Serial2  // Serial Lora
#define Lora_Baud 9600       // Lora Baudrate
#define Serial_WD Serial1    // Serial Wind Direction
#define WD_Baud 9600         // Wind Direction Baudrate
#define WD_RX 4              // Wind Direction RX pin
#define WD_TX 2              // Wind Direction TX pin
#define Lora_RX 16
#define Lora_TX 17

/* Note
Belum yang wave count kalo jadi tinggal disambung pake i2c aja trus
Males OOP
*/

struct dataPacket {
    float temperature, humidity, pressure, speed;
    int waveCount;
    String direction, shoreStatus;
};

dataPacket Telemetry;

// BME VAR
Adafruit_BME280 bme;

// Ultrasonik Var
SoftwareSerial Serial_US(US_RX, US_TX);  // RX, TX
unsigned char data[4] = {};
float distance;

// Wind Speed Var
volatile byte rpmcount;  // hitung signals
volatile unsigned long last_micros;
unsigned long timeold;
unsigned long timemeasure = 10.00;  // detik
int timetoSleep = 1;                // menit
unsigned long sleepTime = 15;       // menit
unsigned long timeNow;
int countUpdate = 0;
float rpm, rotasi_per_detik;        // rotasi/detik
float kecepatan_kilometer_per_jam;  // kilometer/jam
float kecepatan_meter_per_detik;    // meter/detik
volatile boolean flag = false;
unsigned long lora_millis = 0;

void ICACHE_RAM_ATTR rpm_anemometer() {
    flag = true;
}

// Wind Direction Var
String WD_data, s_angin;

void init_BME() {
    Serial.println(F("BME280 test"));
    unsigned status;
    // default settings
    status = bme.begin();
    // You can also pass in a Wire library object like &Wire2
    // status = bme.begin(0x76, &Wire2)
    // if (!status) {
    //     Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
    //     Serial.print("SensorID was: 0x"); Serial.println(bme.sensorID(),16);
    //     Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
    //     Serial.print("   ID of 0x56-0x58 represents a BMP 280,\n");
    //     Serial.print("        ID of 0x60 represents a BME 280.\n");
    //     Serial.print("        ID of 0x61 represents a BME 680.\n");
    //     while (1) delay(10);
    // }
}

void init_Anemometer() {
    pinMode(GPIO_pulse, INPUT_PULLUP);
    digitalWrite(GPIO_pulse, LOW);
    detachInterrupt(digitalPinToInterrupt(GPIO_pulse));                          // memulai Interrupt pada nol
    attachInterrupt(digitalPinToInterrupt(GPIO_pulse), rpm_anemometer, RISING);  // Inisialisasi pin interupt
    rpmcount = 0;
    rpm = 0;
    timeold = 0;
    timeNow = 0;
}

void updateAnemometer(dataPacket& input) {
    if (flag == true) {
        if (long(micros() - last_micros) >= 5000) {
            rpmcount++;
            last_micros = micros();
        }
        flag = false;  // reset flag
    }

    if ((millis() - timeold) >= timemeasure * 1000) {
        countUpdate++;
        detachInterrupt(digitalPinToInterrupt(GPIO_pulse));       // Menonaktifkan interrupt saat menghitung
        rotasi_per_detik = float(rpmcount) / float(timemeasure);  // rotasi per detik
        // kecepatan_meter_per_detik = rotasi_per_detik; // rotasi/detik sebelum dikalibrasi untuk dijadikan meter per detik
        kecepatan_meter_per_detik = ((-0.0181 * (rotasi_per_detik * rotasi_per_detik)) + (1.3859 * rotasi_per_detik) + 1.4055);  // meter/detik sesudah dikalibrasi dan sudah dijadikan meter per detik
        if (kecepatan_meter_per_detik <= 1.5) {                                                                                  // Minimum pembacaan sensor kecepatan angin adalah 1.5 meter/detik
            kecepatan_meter_per_detik = 0.0;
        }
        if (countUpdate == 1)  // kirim data per 10 detik sekali
        {
            input.speed = kecepatan_meter_per_detik;
            countUpdate = 0;
        }
        timeold = millis();
        rpmcount = 0;
        attachInterrupt(digitalPinToInterrupt(GPIO_pulse), rpm_anemometer, RISING);  // enable interrupt
    }
}

void updateBME(dataPacket& input) {
    input.temperature = bme.readTemperature();
    input.pressure = bme.readPressure();
    input.humidity = bme.readHumidity();
}

void updateUS(dataPacket& input) {
    do {
        for (int i = 0; i < 4; i++) {
            data[i] = Serial_US.read();
        }
    } while (Serial_US.read() == 0xff);

    Serial_US.flush();

    if (data[0] == 0xff) {
        int sum;
        sum = (data[0] + data[1] + data[2]) & 0x00FF;
        if (sum == data[3]) {
            distance = (data[1] << 8) + data[2];
            if (distance < Depth_threshold) {
                input.shoreStatus = "PASANG";
            } else {
                input.shoreStatus = "SURUT";
            }
        } else
            Serial.println("ERROR");
    }
}

void updateWD(dataPacket& input) {
    if (Serial_WD.available()) {                // Jika ada data yang diterima dari sensor
        WD_data = Serial_WD.readString();       // data yang diterima dari sensor berawalan tanda * dan diakhiri tanda #, contoh *1#
        int a = WD_data.indexOf("*");           // a adalah index tanda *
        int b = WD_data.indexOf("#");           // b adalah index tanda #
        s_angin = WD_data.substring(a + 1, b);  // membuang tanda * dan # sehingga di dapat nilai dari arah angin
        if (s_angin.equals("1")) {              // jika nilai dari sensor 1 maka arah angin utara
            input.direction = "selatan   ";
        }
        if (s_angin.equals("2")) {
            input.direction = "barat daya";
        }
        if (s_angin.equals("3")) {
            input.direction = "barat     ";
        }
        if (s_angin.equals("4")) {
            input.direction = "barat laut";
        }
        if (s_angin.equals("5")) {
            input.direction = "utara     ";
        }
        if (s_angin.equals("6")) {
            input.direction = "timur laut";
        }
        if (s_angin.equals("7")) {
            input.direction = "timur     ";
        }
        if (s_angin.equals("8")) {
            input.direction = "tenggara  ";
        }
    }
}

void sendData(const dataPacket& input, const String& ID) {  // Send data through Lora
    String Message = (ID + "," +
                      input.shoreStatus + "," +
                      String(input.temperature) + "," +
                      String(input.pressure) + "," +
                      String(input.humidity) + "," +
                      String(input.speed) + "," +
                      input.direction + ";");

    Serial_Lora.println(Message);
    Serial.println(Message);
}

void setup() {
    Serial.begin(115200);
    // Serial_US.begin(US_Baud);
    Serial_WD.begin(WD_Baud, SERIAL_8N1, WD_RX, WD_TX);
    Serial_Lora.begin(Lora_Baud, SERIAL_8N1, Lora_RX, Lora_TX);

    // init_BME();
    init_Anemometer();
}

void loop() {
    updateAnemometer(Telemetry);
    // updateBME(Telemtry);
    // updateUS(Telemtry);
    updateWD(Telemetry);
    sendData(Telemetry, "Jawa");
    delay(1000);
}