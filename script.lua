local http = require("socket.http")
local ltn12 = require("ltn12")
local json = require("dkjson")  -- 使用 dkjson 库来处理 JSON 编码

function on_call(session)
    -- 接听来电
    session:answer()
    
    -- 捕获音频数据
    local audio_file = "/tmp/audio.wav"
    session:recordFile(audio_file, 60, 500, 5)  -- 录音 60 秒

    -- 发送音频数据到中间层 ASR 服务
    local response_body = {}
    local res, code, response_headers = http.request{
        url = "http://localhost:8080/process_asr",  -- 中间层 ASR 服务地址
        method = "POST",
        headers = {
            ["Content-Type"] = "audio/wav",
        },
        source = ltn12.source.file(io.open(audio_file, "rb")),
        sink = ltn12.sink.table(response_body),
    }

    -- 处理 ASR 服务的响应
    if code == 200 then
        local asr_result = table.concat(response_body)
        freeswitch.consoleLog("INFO", "ASR Result: " .. asr_result .. "\n")
        
        -- 将 ASR 结果作为输入发送到 TTS 服务
        local tts_response_body = {}
        local tts_res, tts_code, tts_response_headers = http.request{
            url = "http://localhost:8080/process_tts",  -- 中间层 TTS 服务地址
            method = "POST",
            headers = {
                ["Content-Type"] = "application/json",
            },
            source = ltn12.source.string(json.encode({text = asr_result})),  -- JSON 格式化请求
            sink = ltn12.sink.table(tts_response_body),
        }

        -- 处理 TTS 服务的响应
        if tts_code == 200 then
            local tts_file = "/tmp/tts_output.wav"
            local tts_data = table.concat(tts_response_body)
            
            -- 将响应写入文件
            local file = io.open(tts_file, "wb")
            file:write(tts_data)
            file:close()
            
            -- 播放生成的语音文件
            session:streamFile(tts_file)
        else
            freeswitch.consoleLog("ERR", "TTS Request Failed: " .. tts_code .. "\n")
        end
    else
        freeswitch.consoleLog("ERR", "ASR Request Failed: " .. code .. "\n")
    end

    session:hangup()  -- 通话结束
end
