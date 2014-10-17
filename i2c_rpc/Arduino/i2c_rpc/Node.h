#ifndef ___NODE__H___
#define ___NODE__H___

#include <stdint.h>
#include <EEPROM.h>
#include "Memory.h"
#include "Array.h"
#include "custom_pb.h"
#include "commands_pb.h"
#include "remote_i2c_command.h"
#include "RPCBuffer.h"
#include "NodeCommandProcessor.h"
#define BROADCAST_ADDRESS 0x00


/* Callback functions for slave device. */
extern void i2c_receive_event(int byte_count);
extern void i2c_request_event();


class Node {
public:
  static const uint16_t EEPROM__I2C_ADDRESS = 0x00;
  uint8_t i2c_address_;
  uint8_t output_buffer[32];
  uint8_t command_buffer[32];
  static const uint8_t MIN_I2C_ADDRESS = 0x05;
  static const uint8_t MAX_I2C_ADDRESS = 0x7F;
  i2c_query i2c_query_;

  Node() : i2c_query_({sizeof(output_buffer), output_buffer}) {
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

  //UInt8Array echo_str(UInt8Array msg) { return msg; }
  uint8_t echo_uint8(uint8_t value) { return value; }
  uint32_t echo_uint32(uint32_t value) { return value; }
  int8_t echo_int8(int8_t value) { return value; }
  int32_t echo_int32(int32_t value) { return value; }
  float echo_float(float value) { return value; }

  UInt8Array do_i2c_query(uint8_t address, UInt8Array msg) {
    /* Send an encoded request over I2C and return the encoded response. */
    UInt8Array result = i2c_query_(address, msg);
    return result;
  }

  int32_t test_nanopb_encode_echo_int32(uint8_t address, int32_t value) {
    /* # Encode a protocol buffers message using nano pb #
     *
     * To send requests directly from one device to another, we need to be able
     * to encode the requests on-device.  We do this using nano protocol
     * buffers.  In this method, we aim to test this encoding functionality by
     * conducting the following steps:
     *
     *  1. Encode protocol buffer message using nanopb.
     *  2. Write encoded message to `command_buffer`.
     *  3. Return `UInt8Array` referencing the contents of the encoded message. */
    EchoInt32Message message;

    message.request.value = value;

    i2c_query_.request(address, message, CommandRequest_fields,
                       EchoInt32Request_fields, CommandResponse_fields,
                       EchoInt32Response_fields);

    return message.response.result;
  }

  uint8_t test_nanopb_encode_echo_uint8(uint8_t address, uint8_t value) {
    EchoUint8Message message;

    message.request.value = value;

    i2c_query_.request(address, message, CommandRequest_fields,
                       EchoUint8Request_fields, CommandResponse_fields,
                       EchoUint8Response_fields);

    return message.response.result;
  }

  uint32_t test_nanopb_encode_echo_uint32(uint8_t address, uint32_t value) {
    EchoUint32Message message;

    message.request.value = value;

    i2c_query_.request(address, message, CommandRequest_fields,
                       EchoUint32Request_fields, CommandResponse_fields,
                       EchoUint32Response_fields);

    return message.response.result;
  }

  float test_nanopb_encode_echo_float(float address, float value) {
    EchoFloatMessage message;

    message.request.value = value;

    i2c_query_.request(address, message, CommandRequest_fields,
                       EchoUint32Request_fields, CommandResponse_fields,
                       EchoUint32Response_fields);

    return message.response.result;
  }
};


#endif  // #ifndef ___NODE__H___
