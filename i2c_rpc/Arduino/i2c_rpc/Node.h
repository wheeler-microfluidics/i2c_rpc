#ifndef ___NODE__H___
#define ___NODE__H___

#include <stdint.h>
#include <EEPROM.h>
#include "Memory.h"
#include "Array.h"
#include "custom_pb.h"
#define BROADCAST_ADDRESS 0x00


/* Callback functions for slave device. */
extern void i2c_receive_event(int byte_count);
extern void i2c_request_event();


class Node {
public:
  static const uint16_t EEPROM__I2C_ADDRESS = 0x00;
  uint8_t i2c_address_;
  uint8_t output_buffer[32];
  static const uint8_t MIN_I2C_ADDRESS = 0x05;
  static const uint8_t MAX_I2C_ADDRESS = 0x7F;

  Node() {
    i2c_address_ = EEPROM.read(EEPROM__I2C_ADDRESS);
    Wire.begin(i2c_address_);
  }

  UInt8Array i2c_scan() {
    UInt8Array result;
    result.data = &output_buffer[0];
    result.length = 0;

    for (uint8_t i = MIN_I2C_ADDRESS; i <= MAX_I2C_ADDRESS; i++) {
      Wire.beginTransmission(i);
      if (Wire.endTransmission() == 0) {
        result.data[result.length++] = i;
        delay(1);  // maybe unneeded?
      }
    }
    return result;
  }

  uint32_t ram_free() { return free_memory(); }

  int i2c_address() const { return i2c_address_; }
  int set_i2c_address(uint8_t address) {
    i2c_address_ = address;
    Wire.begin(address);
    // Write the value to the appropriate byte of the EEPROM.
    // These values will remain there when the board is turned off.
    EEPROM.write(EEPROM__I2C_ADDRESS, i2c_address_);
    return address;
  }
  uint8_t ping_pong_uint8(uint8_t value) { return value; }
  uint32_t ping_pong_uint32(uint32_t value) { return value; }
  uint16_t ping_pong_uint16(uint16_t value) { return value; }
  int8_t ping_pong_int8(int8_t value) { return value; }
  int32_t ping_pong_int32(int32_t value) { return value; }
  int16_t ping_pong_int16(int16_t value) { return value; }
  float ping_pong_float(float value) { return value; }
};


#endif  // #ifndef ___NODE__H___
