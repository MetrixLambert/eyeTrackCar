##                        Vuelosophy Eye Tracking Dev-Kit API

### 1.  Basics

#### 1.1 Events

- An application can connect to the dev-kit using socket

- Data and commands are packaged as events using json string

- Event common fields: 

  -   "ty" : EVT_TYPE
  -   "ts":   time stamp long long
  -  "id":    APP_ID

  Where

  ```C
  enum  EVT_TYPE
  {
      EVT_ASK         = 101,
      EVT_ET_MARKER   = 112,
      EVT_HEAD_GESTR  = 113,
      EVT_EYE_GESTR   = 114,
      EVT_IMG = 115,
  };
  enum APP_ID
  {
      APP_ID_BRO = 0,
      APP_ID_FT,
      APP_ID_ET,
      APP_ID_ST,
      APP_ID_SP,
  };
  ```

  

#### 1.2 Ask event 

- Command format

  ```json
  { "ty" :EVT_ASK, "ts":time_stamp_longlong, "id":APP_ID, "cmd":ASK_CMD, "how":ASK_HOW }:
  ```

  Where:

  ```C
  enum ASK_CMD
  {
      ASK_DATA = 1,
  };
  enum ASK_HOW
  {
      ASK_OFF   = 0,
      ASK_ON,
      ASK_ONCE,
      ASK_TOGGLE,
  };
  ```

- Response  format

  ```JSON
  ???
  ```

  

#### 1.3 Head Gesture event

- Format

  ```json
  { "ty" :EVT_HEAD_GESTR, "ts":time_stamp_longlong,  ??? }:
  ```

  Where:

```C
enum HEAD_GESTR_ID
{
    HEAD_GESTR_NONE = 0,
    HEAD_GESTR_NOD_UP,                        //nod up
    HEAD_GESTR_NOD_DW,                        //nod down
    HEAD_GESTR_SHK_LF,                        //shake left
    HEAD_GESTR_SHK_RT,                        //shake right
    HEAD_GESTR_BOB_CC,                        //bobble counter clockwise
    HEAD_GESTR_BOB_CW,                        //bobble clockwise
    HEAD_GESTR_GENERIC,                       //a generic v-turn, without knowledge of axes
};
```

- Response  format

  ```JSON
  ???
  ```

  

#### 1.4 Eye Gesture event

- Format

  ```json
  { "ty" :EVT_EYE_GESTR, "ts":time_stamp_longlong,  ??? }:
  ```

  Where:

```C
enum EYE_GESTR_ID
{ 
   EYE_GESTR_NONE = 0,
   EYE_GESTR_BLINK_START,
   EYE_GESTR_BLINK_END,
};
```

- Response  format

  ```JSON
  ???
  ```

  

#### 1.5 Image event

- Format

  ```json
  { "ty" :EVT_EYE_GESTR, "ts":time_stamp_longlong,  ??? }:
  ```

  Where:

- Response  format

  ```JSON
  ???
  ```

  

### 2.  FT  vcom socket communication

#### 2.1 Open

- IP: FT device IP
- port: 9011

#### 2.2. Ask FT data from vcom socket

- Command - refer section 1.2

  ```JSON
  {"ty":EVT_ASK, "ts":time_stamp_longlong,"id":APP_ID_FT,"cmd":ASK_DATA,"how":ASK_HOW}
  ```

#### 2.3. Receive data from vcom socket

- ET marker event

  ```JSON
  {"ty":EVT_ET_MARKER, "ts":time_stamp_longlong,"id":APP_ID_FT,"x":x_float,"y":y_float}
  ```

  

- Head gesture event

  ```JSON
  {"ty":EVT_HEAD_GESTR, "ts":time_stamp_longlong,"id":APP_ID_FT,"cmd":HEAD_GESTR_ID}
  ```

  

- Eye gesture event

  ```JSON
  {"ty":EVT_EYE_GESTR, "ts":time_stamp_longlong,"id":APP_ID_FT,"cmd":EYE_GESTR_ID}
  ```

  

### 3.  FT  vimg socket communication

#### 3.1 Open

- IP: FT device IP
- port: 9013

#### 3.2. Ask FT image from vimg socket

- Command: 

  ```JSON
  {"ty":EVT_ASK, "ts":time_stamp_longlong,"id":APP_ID_FT,"cmd":ASK_DATA,"how":ASK_HOW}
  ```

  

#### 3.3. Receive image data from vimg socket

- Image event

  ```JSOn
  {"ty":EVT_ET_MARKER, "ts":time_stamp_longlong,"id":APP_ID_FT,"img":"need_to_define"}
  ```

  

