/*
Liang Lu 
This is the file for the ESP32-S3. Build and flash it into the microcontroller. 
Make sure the the IMU is connected properly so that the microcontroller can read the data from it. 
Reference githubs: 
- https://github.com/amiradmehr/IMU/tree/main 
- https://github.com/espressif/esp-idf/blob/v5.3.1/
*/

#include <stdio.h>
#include "unity.h"
#include "driver/i2c.h"
// #include "driver/i2c_master.h"
#include "mpu6050.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_timer.h"

#define I2C_MASTER_SCL_IO 19      /*!< gpio number for I2C master clock */
#define I2C_MASTER_SDA_IO 18      /*!< gpio number for I2C master data  */
#define I2C_MASTER_NUM I2C_NUM_0  /*!< I2C port number for master dev */
#define I2C_MASTER_FREQ_HZ 100000 /*!< I2C master clock frequency */

static const char *TAG = "mpu6050 test";
static mpu6050_handle_t mpu6050 = NULL;
static int64_t start_time_us = 0;

esp_err_t ret;
uint8_t mpu6050_deviceid;
mpu6050_acce_value_t acce;
mpu6050_gyro_value_t gyro;

/**
 * @brief i2c master initialization
 */
static void i2c_bus_init(void)
{
    i2c_config_t conf;
    conf.mode = I2C_MODE_MASTER;
    conf.sda_io_num = (gpio_num_t)I2C_MASTER_SDA_IO;
    conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf.scl_io_num = (gpio_num_t)I2C_MASTER_SCL_IO;
    conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf.master.clk_speed = I2C_MASTER_FREQ_HZ;
    conf.clk_flags = I2C_SCLK_SRC_FLAG_FOR_NOMAL;

    esp_err_t ret = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "I2C config returned error");
        return;
    }

    ret = i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "I2C install returned error");
        return;
    }
}

/**
 * @brief i2c master initialization
 */
static void i2c_sensor_mpu6050_init(void)
{
    esp_err_t ret;

    i2c_bus_init();
    mpu6050 = mpu6050_create(I2C_MASTER_NUM, MPU6050_I2C_ADDRESS);
    if (mpu6050 == NULL)
    {
        ESP_LOGE(TAG, "MPU6050 create returned NULL");
        return;
    }

    ret = mpu6050_config(mpu6050, ACCE_FS_4G, GYRO_FS_500DPS);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "MPU6050 config error");
        return;
    }

    ret = mpu6050_wake_up(mpu6050);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "MPU6050 wake up error");
        return;
    }
}

void get_status() 
{
    ret = mpu6050_get_deviceid(mpu6050, &mpu6050_deviceid);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "Failed to get MPU6050 device ID");
    }

    ret = mpu6050_get_acce(mpu6050, &acce);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "Failed to get accelerometer data");
    }

    ret = mpu6050_get_gyro(mpu6050, &gyro);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "Failed to get gyroscope data");
    }
}

void delete_i2c()
{
    mpu6050_delete(mpu6050);
    ret = i2c_driver_delete(I2C_MASTER_NUM);
    if (ret != ESP_OK)
    {
        ESP_LOGE(TAG, "Failed to delete I2C driver");
    }
}

void log_status()
{
    int64_t elapsed_time_us = esp_timer_get_time() - start_time_us;
    int64_t elapsed_time_s = elapsed_time_us / 1000000;
    int64_t elapsed_time_ms = (elapsed_time_us / 1000) % 1000;

    ESP_LOGI(TAG, "time:%lld.%03lld \n", elapsed_time_s, elapsed_time_ms); 
    // ESP_LOGI(TAG, "acce_x:%.2f, acce_y:%.2f, acce_z:%.2f \n", -acce.acce_x, -acce.acce_y, -acce.acce_z+(2*0.98));
    ESP_LOGI(TAG, "acce_x:%.2f, acce_y:%.2f, acce_z:%.2f \n", acce.acce_x, acce.acce_y, acce.acce_z);
    ESP_LOGI(TAG, "gyro_x:%.2f, gyro_y:%.2f, gyro_z:%.2f \n", gyro.gyro_x, gyro.gyro_y, gyro.gyro_z);
}

void app_main()
{
    i2c_sensor_mpu6050_init();

    if (ret == ESP_OK)
    {
        while (true)
        {
            get_status(); 
            log_status();
            vTaskDelay(10 / portTICK_PERIOD_MS);
        }
    }
    else
    {
        ESP_LOGE(TAG, "Error in setup. Exiting.");
    }
    delete_i2c(); 
}
