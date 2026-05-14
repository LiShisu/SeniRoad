一、建议
前后端各个模块的代码都有一定修改，建议不要pull到本地主分支代码上，避免冲突。

二、整体说明
1.现在所有后端返回格式统一为schemas/base：
class Result(GenericModel, Generic[T]):
    """统一响应结构"""
    code: int  # 业务状态码：200-成功，401-未授权，500-系统错误等
    message: str   # 提示信息
    data: Optional[T] = None # 具体数据内容
2.schemas.exception中定义了一些状态码，后续再完善一下


三、修改说明：
user模块：
Url/接口+表述+状态码设计
前端request.ts设置拦截逻辑，code=200时自动处理包提取data

binding模块：
Url/接口+表述+状态码设计
修复：删除逻辑没有删除数据库数据

favorite-place模块：
Url/接口+表述+状态码设计
亲属端查询传递老人user_id，老人端只要传递activate=true

plan模块
修复：
错误-stream.onData is not a function
401权限错误（gettoken）
sse和框架冲突
前端天气和出行建议格式问题（后端yield返回JSON 字符串，被 json.dumps() 二次转义，前端拿到双层字符串无法正确解析）
注：这里修改了前端sse.ts和后端middleware/logging.py

speech模块：
speech模块->改成了audio
修复：
前端不播报语音：
tts请求失败：llmclient配置问题，原代码手动覆盖 SDK 的底层 URL，注释掉_setup_dashscope中后两行配置
tts阿里云返回数据为空：音频模型似乎不能用，音色也有误，导致无法正常播放，更改配置后成功：DASHSCOPE_TTS_MODEL: str = "cosyvoice-v2"；DASHSCOPE_TTS_VOICE: str = "longxiaochun_v2"
后端正常返回base64前端语音不播报：格式不兼容，解决办法是将base64先写入本地文件然后再播放，但如果文件大小不能超过微信开发助手上限否则报错，于是播放完一条立即清空历史文件。	

navigation模块：
Url/接口+表述+状态码设计
修复了一些功能bug

navigation-records：
Url/接口+表述+状态码设计
修复功能bug，前端正常展示记录（暂未测试删除）

实现voice_navigate语音导航功能：
说明：
微信开发者工具上的录音文件与移动端格式不同，暂时只可在工具上进行播放调试，无法直接播放或者在客户端上播放，录下来后传到后端是损坏的，解析不了；现在保留了处理前端传来录音文件的信息，打通数据通路，但实际上处理的时候用的是我自己在移动设备上录的文件再转.wav。
Recognition适用于实时识别，只能调用realtime模型，但这类模型识别精度非常差，更换成dashscope.MultiModalConversation.call直接调用。
注意：微信助手上“get当前位置”的方法似乎非常粗糙，似乎在学校四区定位到是济南，在图书馆会定位到临沂。选取离当前位置太远的目的地获取不到有效导航路线（建议根据当前位置选择一个比较近的目的地）。

实时定位功能：
因为test_location.py还没通过，正在调试中，不清楚功能是否有bug->暂未重构