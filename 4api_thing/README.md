----------
.evn file put the Claudi api key locally, not hard code in any script

test_api.py is used for test api connect to Claudi


ai_chat.py is used for test api chat with user


config_generator_v2.py can generate device configuration, after you input specific requirement, send it to Claudi api, AI will generate standard config, and return back.


config_checker.py is used for checking configuration, see if there's any suggestions for security, better performance, etc


batch_processor.py 
一次性生成多个配置或检查多个文件


network_assistant.py（主程序）
网络配置管理助手, 整合本周所学，做一个完整的工具集