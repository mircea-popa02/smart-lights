#include <FastLED.h>

#define NUM_LEDS 44
#define DATA_PIN 6

CRGB leds[NUM_LEDS];

void setup()
{
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  Serial.begin(9600);
}

enum Mode
{
  RAINBOW,
  PULSE,
  SOLID,
  IMMERSIVE
};

struct input
{
  Mode mode;
  int delay;
  int r;
  int g;
  int b;
};

struct input parseInput(String input)
{
  struct input parsedInput;

  int commaIndex = input.indexOf(',');
  int mode = input.substring(0, commaIndex).toInt();
  input = input.substring(commaIndex + 1);

  commaIndex = input.indexOf(',');
  int delay = input.substring(0, commaIndex).toInt();
  input = input.substring(commaIndex + 1);

  commaIndex = input.indexOf(',');
  int r = input.substring(0, commaIndex).toInt();
  input = input.substring(commaIndex + 1);

  commaIndex = input.indexOf(',');
  int g = input.substring(0, commaIndex).toInt();
  input = input.substring(commaIndex + 1);

  int b = input.toInt();

  Serial.print("mode: ");
  Serial.println(mode);
  Serial.print("delay: ");
  Serial.println(delay);
  Serial.print("r: ");
  Serial.println(r);
  Serial.print("g: ");
  Serial.println(g);
  Serial.print("b: ");
  Serial.println(b);

  parsedInput.mode = static_cast<Mode>(mode);
  parsedInput.delay = delay;
  parsedInput.r = r;
  parsedInput.g = g;
  parsedInput.b = b;

  return parsedInput;
}

static Mode previousMode = RAINBOW;
static Mode currentMode = RAINBOW;

void loop()
{
  static int currentR = 255;
  static int currentG = 255;
  static int currentB = 255;
  static int brightness = 0;
  static int delta = 1;
  static int animationDelay = 1;
  static int previousColorR = 255;
  static int previousColorG = 255;
  static int previousColorB = 255;

  if (Serial.available() > 0)
  {
    String input = Serial.readStringUntil('\n');
    struct input parsedInput = parseInput(input);

    previousMode = currentMode;

    currentMode = parsedInput.mode;
    currentR = parsedInput.r;
    currentG = parsedInput.g;
    currentB = parsedInput.b;
    animationDelay = parsedInput.delay;
  }

  switch (currentMode)
  {
    case RAINBOW:
    {
      static int hueOffset = 0;
      for (int i = 0; i < NUM_LEDS; i++)
      {
        leds[i] = CHSV((i * 255 / NUM_LEDS + hueOffset) % 255, 255, 255);
      }
      FastLED.show();
      hueOffset++;
      if (hueOffset >= 255)
        hueOffset = 0;
      delay(animationDelay);
    }
    break;

    case PULSE:
    {
      for (int i = 0; i < NUM_LEDS; i++)
      {
        leds[i] = CRGB(currentR * brightness / 255, currentG * brightness / 255, currentB * brightness / 255);
      }
      FastLED.show();
      brightness += delta;
      if (brightness == 255 || brightness == 0)
      {
        delta = -delta;
      }
      delay(animationDelay);
      break;
    }

    case SOLID:
    {
      for (int i = 0; i < NUM_LEDS; i++)
      {
        leds[i] = CRGB(currentR, currentG, currentB);
      }
      FastLED.show();
      break;
    }

    case IMMERSIVE:
    {
      bool updated = false;

      if (currentB != previousColorB)
      {
        previousColorB += (currentB > previousColorB) ? 1 : -1;
        updated = true;
      }

      if (currentG != previousColorG)
      {
        previousColorG += (currentG > previousColorG) ? 1 : -1;
        updated = true;
      }

      if (currentR != previousColorR)
      {
        previousColorR += (currentR > previousColorR) ? 1 : -1;
        updated = true;
      }

      if (updated)
      {
        for (int i = 0; i < NUM_LEDS; i++)
        {
          leds[i] = CRGB(previousColorR, previousColorG, previousColorB);
        }
        FastLED.show();
        delay(animationDelay / 50);
      }
      break;
    }
  }
}
