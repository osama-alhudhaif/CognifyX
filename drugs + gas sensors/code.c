#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/gpio.h"
#include "hardware/rtc.h"
#include "pico/util/datetime.h"

// --- إعداد ساعة الوقت الحقيقي (Real Time Clock) ---
// ملاحظة: البيكو لا يحتفظ بالوقت عند فصل الكهرباء.
// يمكنك ضبط الوقت الحالي يدوياً هنا عند تشغيل الكود لأول مرة:
// الصيغة: (سنة, شهر, يوم, يوم_من_أسبوع, ساعة, دقيقة, ثانية, ميكروثانية)
// مثال: rtc.datetime((2023, 10, 25, 3, 14, 30, 0, 0))

// --- إعداد الحساسات ---
// حساس الغاز القديم على GP26
#define GAS_SENSOR_PIN 26
// حساس المخدرات الجديد على GP27
#define DRUG_SENSOR_PIN 27

// --- إعداد شاشات البار (LED Bar Graphs) ---
// البار الأخضر (للغاز) على GP0 إلى GP9
#define GAS_LED_START 0
// البار الأحمر (للمخدرات) على GP10 إلى GP19
#define DRUG_LED_START 10

// --- إعدادات المعايرة ---
#define RAW_MIN 13475
#define RAW_MAX 64655
#define NUM_LEDS 10

// حساب العتبات
uint16_t THRESHOLD_LEVELS[NUM_LEDS];

void init_thresholds() {
    for (int i = 0; i < NUM_LEDS; i++) {
        THRESHOLD_LEVELS[i] = RAW_MIN + ((RAW_MAX - RAW_MIN) * (i + 1)) / NUM_LEDS;
    }
}

// --- دالة التحديث ---
void update_bar_graph(uint16_t value, int start_pin) {
    for (int i = 0; i < NUM_LEDS; i++) {
        gpio_put(start_pin + i, (value >= THRESHOLD_LEVELS[i]) ? 1 : 0);
    }
}

int main() {
    // تهيئة النظام الأساسي
    stdio_init_all();

    // تهيئة ADC
    adc_init();
    adc_gpio_init(GAS_SENSOR_PIN);
    adc_gpio_init(DRUG_SENSOR_PIN);

    // تهيئة GPIO للـ LEDs
    for (int i = 0; i < NUM_LEDS; i++) {
        gpio_init(GAS_LED_START + i);
        gpio_set_dir(GAS_LED_START + i, GPIO_OUT);
        gpio_init(DRUG_LED_START + i);
        gpio_set_dir(DRUG_LED_START + i, GPIO_OUT);
    }

    // تهيئة RTC
    rtc_init();

    // ضبط الوقت الحالي يدوياً (مثال)
    // datetime_t t = {
    //     .year = 2023,
    //     .month = 10,
    //     .day = 25,
    //     .dotw = 3,  // يوم من الأسبوع (0=أحد, 1=اثنين, etc.)
    //     .hour = 14,
    //     .min = 30,
    //     .sec = 0
    // };
    // rtc_set_datetime(&t);

    // تهيئة العتبات
    init_thresholds();

    printf("System Started - Dual Detection Mode (Gas & Drugs)\n");

    while (true) {
        // 1. جلب الوقت الحالي
        datetime_t t;
        rtc_get_datetime(&t);
        // تنسيق الوقت ليظهر بشكل: HH:MM:SS
        char timestamp[9];
        sprintf(timestamp, "%02d:%02d:%02d", t.hour, t.min, t.sec);

        // 2. قراءة القيم من الحساسين
        adc_select_input(GAS_SENSOR_PIN - 26);  // ADC channel for GP26 is 0
        uint16_t gas_val = adc_read();
        adc_select_input(DRUG_SENSOR_PIN - 26);  // ADC channel for GP27 is 1
        uint16_t drug_val = adc_read();

        // 3. طباعة الوقت مع القيم
        printf("[%s] نسبة الغاز: %u | نسبة المخدرات: %u\n", timestamp, gas_val, drug_val);

        // 4. تحديث المؤشرات الضوئية
        update_bar_graph(gas_val, GAS_LED_START);
        update_bar_graph(drug_val, DRUG_LED_START);

        sleep_ms(1000);
    }

    return 0;
}
