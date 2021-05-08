"""
本文件是用于
1、许栋栋根据行业ID（二级行业），从许栋栋处获取该行业下所有企业的行业知识库
把标准问题和答案存储到cloud_customer_service.rbt_industry_knowledge_lib_init_data表
2、使用聚类分析功能，对表里的数据进行分析，
2.1 接受industry_id作为读入参数，检查数据是否存在，不存在就结束
2.2 设置数据的status=0（重复运行）
2.3 开始进行分析，分级结果以id作为分组依据
2.4 分析完成之后，同组的ID取名：分组1，分组2，以此类推
2.5 分组名更新数据表
2.6 行业数据运行完成之后，这个行业下的数据设置status=1（分析完成）
3、分析结果数据会显示到saas管理平台：
【机器人行业库】-【初始行业库】
4、界面上进行【处理】操作：把数据添加到行业库
处理之后，把这个数据的status=2
"""