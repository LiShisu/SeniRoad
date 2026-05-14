export type SSEEventType = string;

export interface SSEEvent<T = any> {
  event: SSEEventType;
  data: T;
}

export interface SSEConfig {
  url: string;
  method?: string;
  data?: any;
  headers?: Record<string, string>;
}

export interface SSECallbacks<T = any> {
  onEvent?: (event: SSEEventType, data: T) => void;
  onComplete?: (data: T) => void;
  onError?: (error: any) => void;
}
// 【修复 1】：手写一个兼容性 100% 的 UTF-8 解码器，彻底告别 TextDecoder 报错
function decodeUTF8(arrayBuffer: ArrayBuffer): string {
  const bytes = new Uint8Array(arrayBuffer);
  let out = '';
  let i = 0;
  const len = bytes.length;
  while (i < len) {
    let c = bytes[i++];
    switch (c >> 4) {
      case 0: case 1: case 2: case 3: case 4: case 5: case 6: case 7:
        out += String.fromCharCode(c);
        break;
      case 12: case 13:
        let char2 = bytes[i++];
        out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F));
        break;
      case 14:
        let char2a = bytes[i++];
        let char3 = bytes[i++];
        out += String.fromCharCode(((c & 0x0F) << 12) | ((char2a & 0x3F) << 6) | ((char3 & 0x3F) << 0));
        break;
    }
  }
  return out;
}
export class SSEClient<T = any> {
  private url: string;
  private method: string;
  private data: any;
  private headers: Record<string, string>;
  private requestTask: any;
  private buffer: string;
  private result: Partial<T>;

  constructor(config: SSEConfig) {
    this.url = config.url;
    this.method = config.method || 'POST';
    this.data = config.data || {};
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      ...(config.headers || {})
    };
    this.buffer = '';
    this.result = {};
  }

  connect(callbacks: SSECallbacks<T>): () => void {
    const { onEvent, onComplete, onError } = callbacks;
    
    const requestOptions: any = {
      url: this.url,
      method: this.method as any,
      data: typeof this.data === 'string' ? this.data : JSON.stringify(this.data),
      header: this.headers,
      enableChunked: true, // 核心：开启分块传输
      // responseType: 'stream',
      // success: (res: any) => {
      //   const stream = res.data;
        
      //   stream.onData((chunk: string) => {
      //     this.buffer += chunk;
      //     this.parseEvents(onEvent, onComplete, onError);
      //   });
      success: (res: any) => {
        // 请求成功结束时触发
        if (!this.hasCompleteEvent && onComplete) {
           onComplete(this.result as T);
        }
      },
      fail: (err: any) => {
        if (onError) onError(err);
      }
    };
    this.requestTask = wx.request(requestOptions);
if (this.requestTask) {
  this.requestTask.onChunkReceived((res: any) => {
    try {
      // 使用我们自己写的解码器
      const chunk = decodeUTF8(res.data);
      this.buffer += chunk;
      this.parseEvents(onEvent, onComplete, onError);
    } catch (err) {
      console.error('SSE 流数据解码失败:', err);
    }
  });
}

return () => {
  this.abort();
};
}

  private hasCompleteEvent = false;

  private parseEvents(
    onEvent?: (event: SSEEventType, data: any) => void,
    onComplete?: (data: T) => void,
    onError?: (error: any) => void
  ) {
    const lines = this.buffer.split('\n');
    let eventType: SSEEventType | null = null;
    let eventDataStr = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      if (line.startsWith('event:')) {
        eventType = line.substring(6).trim();
      } else if (line.startsWith('data:')) {
        eventDataStr = line.substring(5).trim();
      } else if (line === '' && eventType && eventDataStr) {
        let eventData;
        try {
          eventData = JSON.parse(eventDataStr);
        } catch {
          eventData = eventDataStr;
        }
        this.accumulateResult(eventType, eventData);

        if (onEvent) {
          onEvent(eventType, eventData);
        }

        if (eventType === 'complete') {
          this.hasCompleteEvent = true;
          if (onComplete) {
            onComplete(this.result as T);
          }
          this.closeStream();
          return;
        } else if (eventType === 'error') {
          if (onError) {
            onError(eventData);
          }
          this.closeStream();
          return;
        }

        eventType = null;
        eventDataStr = '';
      }
    }

    const lastEmptyIndex = this.buffer.lastIndexOf('\n\n');
    if (lastEmptyIndex !== -1) {
      this.buffer = this.buffer.substring(lastEmptyIndex + 2);
    }
  }

  private accumulateResult(eventType: SSEEventType, data: any) {
    if (eventType === 'destination') {
      this.result = { ...this.result, ...data };
    } else if (eventType === 'route') {
      (this.result as any).route = data;
    } else if (eventType === 'weather') {
      (this.result as any).weather = data;
    } else if (eventType === 'advice') {
      (this.result as any).navigation_advice = data;
    } else if (eventType === 'complete') {
      this.result = { ...this.result, ...data };
    }
  }

  private closeStream() {
    if (this.requestTask?.data?.close) {
      this.requestTask.data.close();
    }
  }

  abort() {
    if (this.requestTask?.abort) {
      this.requestTask.abort();
    }
  }
}

export function createSSEStream<T = any>(
  config: SSEConfig,
  callbacks: SSECallbacks<T>
): () => void {
  const client = new SSEClient<T>(config);
  return client.connect(callbacks);
}

// 旧版SSE:
// export type SSEEventType = string;



// export interface SSEEvent<T = any> {

//   event: SSEEventType;

//   data: T;

// }



// export interface SSEConfig {

//   url: string;

//   method?: string;

//   data?: any;

//   headers?: Record<string, string>;

// }



// export interface SSECallbacks<T = any> {

//   onEvent?: (event: SSEEventType, data: T) => void;

//   onComplete?: (data: T) => void;

//   onError?: (error: any) => void;

// }



// export class SSEClient<T = any> {

//   private url: string;

//   private method: string;

//   private data: any;

//   private headers: Record<string, string>;

//   private requestTask: any;

//   private buffer: string;

//   private result: Partial<T>;



//   constructor(config: SSEConfig) {

//     this.url = config.url;

//     this.method = config.method || 'POST';

//     this.data = config.data || {};

//     this.headers = {

//       'Content-Type': 'application/json',

//       'Accept': 'text/event-stream',

//       ...(config.headers || {})

//     };

//     this.buffer = '';

//     this.result = {};

//   }



//   connect(callbacks: SSECallbacks<T>): () => void {

//     const { onEvent, onComplete, onError } = callbacks;

   

//     this.requestTask = wx.request({

//       url: this.url,

//       method: this.method,

//       data: typeof this.data === 'string' ? this.data : JSON.stringify(this.data),

//       header: this.headers,

//       responseType: 'stream',

//       success: (res: any) => {

//         const stream = res.data;

       

//         stream.onData((chunk: string) => {

//           this.buffer += chunk;

//           this.parseEvents(onEvent, onComplete, onError);

//         });

       

//         stream.onEnd(() => {

//           if (onError && !this.hasCompleteEvent) {

//             onError(new Error('Stream ended without complete event'));

//           }

//         });

       

//         stream.onError((err: any) => {

//           if (onError) {

//             onError(err);

//           }

//         });

//       },

//       fail: (err: any) => {

//         if (onError) {

//           onError(err);

//         }

//       }

//     });



//     return () => {

//       this.abort();

//     };

//   }



//   private hasCompleteEvent = false;



//   private parseEvents(

//     onEvent?: (event: SSEEventType, data: any) => void,

//     onComplete?: (data: Partial<T>) => void,

//     onError?: (error: any) => void

//   ) {

//     const lines = this.buffer.split('\n');

//     let eventType: SSEEventType | null = null;

//     let eventDataStr = '';



//     for (let i = 0; i < lines.length; i++) {

//       const line = lines[i];



//       if (line.startsWith('event:')) {

//         eventType = line.substring(6).trim();

//       } else if (line.startsWith('data:')) {

//         eventDataStr = line.substring(5).trim();

//       } else if (line === '' && eventType && eventDataStr) {

//         let eventData;

//         try {

//           eventData = JSON.parse(eventDataStr);

//         } catch {

//           eventData = eventDataStr;

//         }



//         this.accumulateResult(eventType, eventData);



//         if (onEvent) {

//           onEvent(eventType, eventData);

//         }



//         if (eventType === 'complete') {

//           this.hasCompleteEvent = true;

//           if (onComplete) {

//             onComplete(this.result);

//           }

//           this.closeStream();

//           return;

//         } else if (eventType === 'error') {

//           if (onError) {

//             onError(eventData);

//           }

//           this.closeStream();

//           return;

//         }



//         eventType = null;

//         eventDataStr = '';

//       }

//     }



//     const lastEmptyIndex = this.buffer.lastIndexOf('\n\n');

//     if (lastEmptyIndex !== -1) {

//       this.buffer = this.buffer.substring(lastEmptyIndex + 2);

//     }

//   }



//   private accumulateResult(eventType: SSEEventType, data: any) {

//     if (eventType === 'destination') {

//       this.result = { ...this.result, ...data };

//     } else if (eventType === 'route') {

//       (this.result as any).route = data;

//     } else if (eventType === 'weather') {

//       (this.result as any).weather = data;

//     } else if (eventType === 'advice') {

//       (this.result as any).navigation_advice = data;

//     } else if (eventType === 'complete') {

//       this.result = { ...this.result, ...data };

//     }

//   }



//   private closeStream() {

//     if (this.requestTask?.data?.close) {

//       this.requestTask.data.close();

//     }

//   }



//   abort() {

//     if (this.requestTask?.abort) {

//       this.requestTask.abort();

//     }

//   }

// }



// export function createSSEStream<T = any>(

//   config: SSEConfig,

//   callbacks: SSECallbacks<T>

// ): () => void {

//   const client = new SSEClient<T>(config);

//   return client.connect(callbacks);

// }