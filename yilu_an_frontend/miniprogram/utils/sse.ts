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
    
    this.requestTask = wx.request({
      url: this.url,
      method: this.method,
      data: typeof this.data === 'string' ? this.data : JSON.stringify(this.data),
      header: this.headers,
      responseType: 'stream',
      success: (res: any) => {
        const stream = res.data;
        
        stream.onData((chunk: string) => {
          this.buffer += chunk;
          this.parseEvents(onEvent, onComplete, onError);
        });
        
        stream.onEnd(() => {
          if (onError && !this.hasCompleteEvent) {
            onError(new Error('Stream ended without complete event'));
          }
        });
        
        stream.onError((err: any) => {
          if (onError) {
            onError(err);
          }
        });
      },
      fail: (err: any) => {
        if (onError) {
          onError(err);
        }
      }
    });

    return () => {
      this.abort();
    };
  }

  private hasCompleteEvent = false;

  private parseEvents(
    onEvent?: (event: SSEEventType, data: any) => void,
    onComplete?: (data: Partial<T>) => void,
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
            onComplete(this.result);
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