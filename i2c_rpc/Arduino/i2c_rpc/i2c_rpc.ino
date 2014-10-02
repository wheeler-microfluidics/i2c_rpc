#include "EEPROM.h"
#include "Wire.h"
#include "Memory.h"
#include "I2CHandler.h"
#include "nanopb.h"
#include "NadaMQ.h"
#include "ArduinoRPC.h"
#include "Array.h"
#include "Node.h"
#include "NodeCommandProcessor.h"
#include "packet_handler.h"


#define PACKET_SIZE   64
#define COMMAND_ARRAY_BUFFER_SIZE   56
/* To save RAM, the serial-port interface may be disabled by defining
 * `DISABLE_SERIAL`. */
#ifndef DISABLE_SERIAL
uint8_t packet_buffer[PACKET_SIZE];
#endif  // #ifndef DISABLE_SERIAL

uint8_t i2c_packet_buffer[PACKET_SIZE];

/*  - Allocate buffer for command-processor to extract/write array data. */
uint8_t command_array_buffer[COMMAND_ARRAY_BUFFER_SIZE];
UInt8Array command_array = {COMMAND_ARRAY_BUFFER_SIZE,
                            &command_array_buffer[0]};

Node node;
CommandProcessor<Node> command_processor(node, command_array);

#ifndef DISABLE_SERIAL
typedef CommandPacketHandler<Stream, CommandProcessor<Node> > Handler;
typedef PacketReactor<PacketParser<FixedPacket>, Stream, Handler> Reactor;

FixedPacket packet;
/* `reactor` maintains parse state for a packet, and updates state one-byte
 * at-a-time. */
PacketParser<FixedPacket> parser;
/* `handler` processes complete packets and sends response as necessary. */
Handler handler(Serial, command_processor);
/* `reactor` uses `parser` to parse packets from input stream and passes
 * complete packets to `handler` for processing. */
Reactor reactor(parser, Serial, handler);
#endif  // #ifndef DISABLE_SERIAL


void setup() {
#ifdef __AVR_ATmega2560__
  /* Join I2C bus as master. */
  Wire.begin();
#else
  /* Join I2C bus as slave. */
  Wire.onReceive(&I2CHandlerClass::i2c_receive_event);
  Wire.onRequest(&I2CHandlerClass::i2c_request_event);
#endif  // #ifdef __AVR_ATmega328__
  // Set i2c clock-rate to 400kHz.
  TWBR = 12;
#if !defined(DISABLE_SERIAL)
  Serial.begin(115200);
  packet.reset_buffer(PACKET_SIZE, &packet_buffer[0]);
  parser.reset(&packet);
#endif  // #ifndef DISABLE_SERIAL
  I2CHandler.begin(i2c_packet_buffer, PACKET_SIZE);
}


void loop() {
#ifndef DISABLE_SERIAL
  /* Parse all new bytes that are available.  If the parsed bytes result in a
   * completed packet, pass the complete packet to the command-processor to
   * process the request. */
  reactor.parse_available();
#endif  // #ifndef DISABLE_SERIAL
  I2CHandler.parse_available(command_processor);
}
