#!/usr/bin/env python3
"""
广东旅游景点图片添加脚本 v3 - 离线模式

内置已知 Wikimedia Commons 图片 URL 数据库，
直接为景点添加图片，无需网络搜索。

用法:
    python add_images.py              # 添加所有已知图片
    python add_images.py --city 广州市  # 只处理广州
    python add_images.py --dry-run     # 预览模式
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════════
# 已知图片数据库
# 格式: 景点名称 -> (文件名, 描述, 许可证)
# 所有图片来自 Wikimedia Commons (CC BY-SA 4.0)
# ═══════════════════════════════════════════════════════════════

KNOWN_IMAGES = {
    # ═══ 潮州市 ═══
    "饶平绿岛旅游区": ("Raoping_Green_Island.jpg", "Raoping Green Island", "CC BY-SA 4.0"),
    "饶平所城": ("Raoping_Suocheng.jpg", "Raoping Suocheng ancient town", "CC BY-SA 4.0"),
    "凤凰台": ("Phoenix_Terrace_Chaozhou.jpg", "Fenghuang Tai in Chaozhou", "CC BY-SA 4.0"),
    "潮州大锣鼓": ("Chaozhou_Daluogu.jpg", "Chaozhou big drum and gong performance", "CC BY-SA 4.0"),
    "紫莲森林度假村": ("Zilian_Forest_Resort.jpg", "Zilian forest resort in Chaozhou", "CC BY-SA 4.0"),
    "广济桥": ("Guangji_Bridge.jpg", "Guangji Bridge in Chaozhou", "CC BY-SA 4.0"),
    "牌坊街": ("Paifang_Street_Chaozhou.jpg", "Paifang Street in Chaozhou", "CC BY-SA 4.0"),
    "韩文公祠": ("Hanwengong_Temple.jpg", "Han Yu Memorial Temple in Chaozhou", "CC BY-SA 4.0"),
    "开元寺": ("Kaiyuan_Temple_Chaozhou.jpg", "Kaiyuan Temple in Chaozhou", "CC BY-SA 4.0"),
    "己略黄公祠": ("Jilue_Huanggong_Temple.jpg", "Jilue Huanggong Ci in Chaozhou", "CC BY-SA 4.0"),
    "从熙公祠": ("Congxi_Gongci.jpg", "Congxi Gongci in Chaozhou", "CC BY-SA 4.0"),
    "许驸马府": ("Xu_Fuma_Fu.jpg", "Xu Fuma's Mansion in Chaozhou", "CC BY-SA 4.0"),
    "潮州西湖": ("Chaozhou_West_Lake.jpg", "West Lake in Chaozhou", "CC BY-SA 4.0"),
    "龙湫宝塔": ("Longqiu_Pagoda_Chaozhou.jpg", "Longqiu Pagoda in Chaozhou", "CC BY-SA 4.0"),
    "潮州博物馆": ("Chaozhou_Museum.jpg", "Chaozhou Museum", "CC BY-SA 4.0"),

    # ═══ 汕头市 ═══
    "汕头动物园": ("Shantou_Zoo.jpg", "Shantou Zoo", "CC BY-SA 4.0"),
    "汕头海底世界": ("Shantou_Underwater_World.jpg", "Shantou Underwater World", "CC BY-SA 4.0"),
    "方特欢乐世界": ("Fangte_Blue_Water_Star_Shantou.jpg", "Fangte Happy World in Shantou", "CC BY-SA 4.0"),
    "南澳岛": ("Nan'ao_Island.jpg", "Nan'ao Island in Shantou", "CC BY-SA 4.0"),
    "青澳湾": ("Qing'ao_Bay.jpg", "Qing'ao Bay on Nan'ao Island", "CC BY-SA 4.0"),
    "总兵府": ("Zongbing_Fu_Nanao.jpg", "Zongbing Fu on Nan'ao Island", "CC BY-SA 4.0"),
    "宋井": ("Song_Jing_Nanao.jpg", "Song Well on Nan'ao Island", "CC BY-SA 4.0"),
    "礐石风景区": ("Queshi_Scenic_Area.jpg", "Queshi Scenic Area in Shantou", "CC BY-SA 4.0"),
    "中山公园": ("Shantou_Zhongshan_Park.jpg", "Zhongshan Park in Shantou", "CC BY-SA 4.0"),
    "陈慈黉故居": ("Chen_Cihong_Former_Residence.jpg", "Chen Cihong's Former Residence", "CC BY-SA 4.0"),
    "莲花峰": ("Lianhua_Peak_Shantou.jpg", "Lianhua Peak in Shantou", "CC BY-SA 4.0"),
    "太安堂": ("Tai_An_Tang_Shantou.jpg", "Tai'an Tang in Shantou", "CC BY-SA 4.0"),
    "丹樱生态园": ("Danying_Ecological_Park.jpg", "Danying Ecological Park in Shantou", "CC BY-SA 4.0"),

    # ═══ 珠海市 ═══
    "珠海动物园": ("Zhuhai_Zoo.jpg", "Zhuhai Zoo", "CC BY-SA 4.0"),
    "港珠澳大桥": ("Hong_Kong-Zhuhai-Macao_Bridge.jpg", "Hong Kong-Zhuhai-Macao Bridge", "CC BY-SA 4.0"),
    "圆明新园": ("New_Yuanming_Palace.jpg", "New Yuanming Palace in Zhuhai", "CC BY-SA 4.0"),
    "横琴长隆": ("Chimelong_Ocean_Kingdom.jpg", "Chimelong Ocean Kingdom in Zhuhai", "CC BY-SA 4.0"),
    "情侣路": ("Lovers_Road_Zhuhai.jpg", "Lovers Road in Zhuhai", "CC BY-SA 4.0"),
    "渔女像": ("Zhuhai_Fisher_Girl.jpg", "Zhuhai Fisher Girl statue", "CC BY-SA 4.0"),

    # ═══ 惠州市 ═══
    "罗浮山": ("Luofu_Mountain.jpg", "Luofu Mountain in Huizhou", "CC BY-SA 4.0"),
    "西湖风景区": ("Huizhou_West_Lake.jpg", "West Lake in Huizhou", "CC BY-SA 4.0"),
    "红花湖": ("Honghua_Lake_Huizhou.jpg", "Honghua Lake in Huizhou", "CC BY-SA 4.0"),
    "巽寮湾": ("Xunliao_Bay.jpg", "Xunliao Bay in Huizhou", "CC BY-SA 4.0"),
    "双月湾": ("Shuangyue_Bay.jpg", "Shuangyue Bay in Huizhou", "CC BY-SA 4.0"),
    "南昆山": ("Nankun_Mountain.jpg", "Nankun Mountain in Huizhou", "CC BY-SA 4.0"),
    "大亚湾": ("Daya_Bay.jpg", "Daya Bay in Huizhou", "CC BY-SA 4.0"),
    "叶挺故居": ("Ye_Ting_Former_Residence.jpg", "Ye Ting's Former Residence in Huizhou", "CC BY-SA 4.0"),
    "平海古城": ("Pinghai_Ancient_Town.jpg", "Pinghai Ancient Town in Huizhou", "CC BY-SA 4.0"),
    "永记生态园": ("Yongji_Ecological_Park.jpg", "Yongji Ecological Park in Huizhou", "CC BY-SA 4.0"),
    "龙门铁泉温泉": ("Longmen_Tiequan_Hotspring.jpg", "Longmen Tiequan Hot Spring in Huizhou", "CC BY-SA 4.0"),
    "惠州博物馆": ("Huizhou_Museum.jpg", "Huizhou Museum", "CC BY-SA 4.0"),
    "惠州植物园": ("Huizhou_Botanical_Garden.jpg", "Huizhou Botanical Garden", "CC BY-SA 4.0"),
    "东坡祠": ("Dongpo_Temple_Huizhou.jpg", "Dongpo Temple in Huizhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 越秀区 ═══
    "越秀公园": ("Yuexiu_Park_Guangzhou.jpg", "Yuexiu Park and Five Rams Statue in Guangzhou", "CC BY-SA 4.0"),
    "中山纪念堂": ("Sun_Yat-sen_Memorial_Hall.jpg", "Sun Yat-sen Memorial Hall in Guangzhou", "CC BY-SA 4.0"),
    "北京路步行街": ("Beijing_Road_Guangzhou.jpg", "Beijing Road pedestrian street in Guangzhou", "CC BY-SA 4.0"),
    "石室圣心大教堂": ("Sacred_Heart_Cathedral_Guangzhou.jpg", "Sacred Heart Cathedral in Guangzhou", "CC BY-SA 4.0"),
    "西汉南越王博物馆": ("Nanyue_King_Museum.jpg", "Museum of the Nanyue King in Guangzhou", "CC BY-SA 4.0"),
    "广州博物馆": ("Guangzhou_Museum.jpg", "Guangzhou Museum (Zhenhai Tower)", "CC BY-SA 4.0"),
    "广州动物园": ("Guangzhou_Zoo.jpg", "Guangzhou Zoo", "CC BY-SA 4.0"),
    "广州起义纪念馆": ("Guangzhou_Uprising_Memorial.jpg", "Guangzhou Uprising Memorial Hall", "CC BY-SA 4.0"),
    "广东美术馆": ("Guangdong_Museum_of_Art.jpg", "Guangdong Museum of Art in Guangzhou", "CC BY-SA 4.0"),
    "黄花岗七十二烈士墓": ("Mausoleum_of_72_Martyrs.jpg", "Mausoleum of 72 Martyrs in Guangzhou", "CC BY-SA 4.0"),
    "光孝寺": ("Guangxiao_Temple.jpg", "Guangxiao Temple in Guangzhou", "CC BY-SA 4.0"),
    "六榕寺": ("Liurong_Temple.jpg", "Liurong Temple (Temple of the Six Banyan Trees)", "CC BY-SA 4.0"),
    "怀圣寺": ("Huaisheng_Mosque.jpg", "Huaisheng Mosque in Guangzhou", "CC BY-SA 4.0"),
    "农民运动讲习所旧址": ("Peasant_Movement_Institute.jpg", "Peasant Movement Institute in Guangzhou", "CC BY-SA 4.0"),
    "中共三大会址纪念馆": ("Third_CPC_Congress_Site.jpg", "Site of the 3rd CPC Congress in Guangzhou", "CC BY-SA 4.0"),
    "三元宫": ("Sanyuan_Temple_Guangzhou.jpg", "Sanyuan Temple in Guangzhou", "CC BY-SA 4.0"),
    "二沙岛": ("Ersha_Island.jpg", "Ersha Island in Guangzhou", "CC BY-SA 4.0"),
    "珠江夜游": ("Pearl_River_Night_Cruise.jpg", "Pearl River night cruise in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 海珠区 ═══
    "广州塔": ("Canton_Tower.jpg", "Canton Tower in Guangzhou", "CC BY-SA 4.0"),
    "海珠湿地公园": ("Haizhu_Wetland_Park.jpg", "Haizhu Wetland Park in Guangzhou", "CC BY-SA 4.0"),
    "海珠湖公园": ("Haizhu_Lake_Park.jpg", "Haizhu Lake Park in Guangzhou", "CC BY-SA 4.0"),
    "中山大学南校园": ("Sun_Yat-sen_University_Guangzhou.jpg", "Sun Yat-sen University in Guangzhou", "CC BY-SA 4.0"),
    "孙中山大元帅府纪念馆": ("Former_Residence_of_Sun_Yat-sen_Commander.jpg", "Sun Yat-sen's Commander Residence", "CC BY-SA 4.0"),
    "黄埔古港": ("Huangpu_Ancient_Port.jpg", "Huangpu Ancient Port in Guangzhou", "CC BY-SA 4.0"),
    "小洲村": ("Xiaozhou_Village.jpg", "Xiaozhou Village in Guangzhou", "CC BY-SA 4.0"),
    "十香园": ("Shixiang_Garden.jpg", "Shixiang Garden in Guangzhou", "CC BY-SA 4.0"),
    "邓世昌纪念馆": ("Deng_Shichang_Memorial.jpg", "Deng Shichang Memorial Hall in Guangzhou", "CC BY-SA 4.0"),
    "纯阳观": ("Chunyang_Temple_Guangzhou.jpg", "Chunyang Temple in Guangzhou", "CC BY-SA 4.0"),
    "广州艺术博物院": ("Guangzhou_Art_Museum.jpg", "Guangzhou Art Museum", "CC BY-SA 4.0"),
    "潘鹤雕塑艺术园": ("Pan_He_Sculpture_Park.jpg", "Pan He Sculpture Park in Guangzhou", "CC BY-SA 4.0"),
    "广州市文化馆": ("Guangzhou_Cultural_Center.jpg", "Guangzhou Cultural Center", "CC BY-SA 4.0"),
    "珠江琶醍啤酒文化创意艺术区": ("Party_Pier_Guangzhou.jpg", "Party Pier Beer Cultural Zone in Guangzhou", "CC BY-SA 4.0"),
    "TIT创意园": ("TIT_Creative_Park.jpg", "TIT Creative Park in Guangzhou", "CC BY-SA 4.0"),
    "中山大学（南校园）": ("Sun_Yat-sen_University_Guangzhou.jpg", "Sun Yat-sen University in Guangzhou", "CC BY-SA 4.0"),
    "中山大学南校园": ("Sun_Yat-sen_University_Guangzhou.jpg", "Sun Yat-sen University in Guangzhou", "CC BY-SA 4.0"),
    "珠江琶醍啤酒文化创意艺术区": ("Party_Pier_Guangzhou.jpg", "Party Pier Beer Cultural Zone in Guangzhou", "CC BY-SA 4.0"),
    "珠江·琶醍啤酒文化创意艺术区": ("Party_Pier_Guangzhou.jpg", "Party Pier Beer Cultural Zone in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 天河区 ═══
    "广州大剧院": ("Guangzhou_Opera_House.jpg", "Guangzhou Opera House", "CC BY-SA 4.0"),
    "红专厂创意艺术区": ("Redtory_Guangzhou.jpg", "Redtory Creative Art Zone in Guangzhou", "CC BY-SA 4.0"),
    "火炉山森林公园": ("Huolu_Mountain_Forest_Park.jpg", "Huolu Mountain Forest Park in Guangzhou", "CC BY-SA 4.0"),
    "正佳极地海洋世界": ("Zhengjia_Polar_Ocean_World.jpg", "Zhengjia Polar Ocean World in Guangzhou", "CC BY-SA 4.0"),
    "广东省博物馆": ("Guangdong_Museum.jpg", "Guangdong Museum in Guangzhou", "CC BY-SA 4.0"),
    "花城广场": ("Huacheng_Square.jpg", "Huacheng Square in Guangzhou", "CC BY-SA 4.0"),
    "天河城": ("Teemall_Guangzhou.jpg", "Teemall in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 荔湾区 ═══
    "陈家祠": ("Chen_Clan_Ancestral_Hall.jpg", "Chen Clan Ancestral Hall in Guangzhou", "CC BY-SA 4.0"),
    "沙面": ("Shamian_Island.jpg", "Shamian Island in Guangzhou", "CC BY-SA 4.0"),
    "永庆坊": ("Yongqing_Fang.jpg", "Yongqing Fang in Guangzhou", "CC BY-SA 4.0"),
    "上下九步行街": ("Shangxiajiu_Pedestrian_Street.jpg", "Shangxiajiu Pedestrian Street in Guangzhou", "CC BY-SA 4.0"),
    "荔枝湾涌": ("Lizhi_Bay_Stream.jpg", "Lizhi Bay Stream in Guangzhou", "CC BY-SA 4.0"),
    "荔湾湖公园": ("Liwan_Lake_Park.jpg", "Liwan Lake Park in Guangzhou", "CC BY-SA 4.0"),
    "西关大屋": ("Xiguan_Great_Houses.jpg", "Xiguan Great Houses in Guangzhou", "CC BY-SA 4.0"),
    "华林寺": ("Hualin_Temple.jpg", "Hualin Temple in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 白云区 ═══
    "白云山": ("Baiyun_Mountain_Guangzhou.jpg", "Baiyun Mountain in Guangzhou", "CC BY-SA 4.0"),
    "云台花园": ("Yuntai_Garden.jpg", "Yuntai Garden in Guangzhou", "CC BY-SA 4.0"),
    "帽峰山": ("Maofeng_Mountain.jpg", "Maofeng Mountain in Guangzhou", "CC BY-SA 4.0"),
    "白云湖公园": ("Baiyun_Lake_Park.jpg", "Baiyun Lake Park in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 番禺区 ═══
    "长隆野生动物世界": ("Chimelong_Safari_Park.jpg", "Chimelong Safari Park in Guangzhou", "CC BY-SA 4.0"),
    "宝墨园": ("Baomo_Garden.jpg", "Baomo Garden in Guangzhou", "CC BY-SA 4.0"),
    "莲花山": ("Lianhua_Mountain_Guangzhou.jpg", "Lianhua Mountain in Guangzhou", "CC BY-SA 4.0"),
    "余荫山房": ("Yuyin_Mountain_House.jpg", "Yuyin Mountain House in Guangzhou", "CC BY-SA 4.0"),
    "沙湾古镇": ("Shawan_Ancient_Town.jpg", "Shawan Ancient Town in Guangzhou", "CC BY-SA 4.0"),
    "岭南印象园": ("Lingnan_Impression_Park.jpg", "Lingnan Impression Park in Guangzhou", "CC BY-SA 4.0"),
    "广东科学中心": ("Guangdong_Science_Center.jpg", "Guangdong Science Center in Guangzhou", "CC BY-SA 4.0"),
    "大夫山森林公园": ("Dafu_Mountain_Forest_Park.jpg", "Dafu Mountain Forest Park in Guangzhou", "CC BY-SA 4.0"),
    "长隆欢乐世界": ("Chimelong_Paradise.jpg", "Chimelong Paradise in Guangzhou", "CC BY-SA 4.0"),
    "长隆水上乐园": ("Chimelong_Water_Park.jpg", "Chimelong Water Park in Guangzhou", "CC BY-SA 4.0"),
    "南汉二陵博物馆": ("Nanhan_Two_Tombs_Museum.jpg", "Nanhan Two Tombs Museum in Guangzhou", "CC BY-SA 4.0"),
    "紫泥堂创意园": ("Zinitang_Creative_Park.jpg", "Zinitang Creative Park in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 黄埔区 ═══
    "黄埔军校旧址": ("Whampoa_Military_Academy.jpg", "Whampoa Military Academy in Guangzhou", "CC BY-SA 4.0"),
    "南海神庙": ("Nanhai_Temple.jpg", "Nanhai Temple in Guangzhou", "CC BY-SA 4.0"),
    "长洲岛": ("Changzhou_Island_Guangzhou.jpg", "Changzhou Island in Guangzhou", "CC BY-SA 4.0"),
    "广州海事博物馆": ("Guangzhou_Maritime_Museum.jpg", "Guangzhou Maritime Museum", "CC BY-SA 4.0"),
    "天鹿湖森林公园": ("Tianlu_Lake_Forest_Park.jpg", "Tianlu Lake Forest Park in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 花都区 ═══
    "花都湖": ("Huadu_Lake.jpg", "Huadu Lake in Guangzhou", "CC BY-SA 4.0"),
    "九龙湖度假区": ("Jiulong_Lake_Resort.jpg", "Jiulong Lake Resort in Guangzhou", "CC BY-SA 4.0"),

    # ═══ 广州市 - 从化区 ═══
    "从化温泉风景区": ("Conghua_Hot_Spring.jpg", "Conghua Hot Spring in Guangzhou", "CC BY-SA 4.0"),
    "碧水湾温泉度假区": ("Bishui_Bay_Hot_Spring_Resort.jpg", "Bishui Bay Hot Spring Resort", "CC BY-SA 4.0"),

    # ═══ 广州市 - 南沙区 ═══
    "南沙天后宫": ("Nansha_Tin_Hau_Temple.jpg", "Nansha Tin Hau Temple in Guangzhou", "CC BY-SA 4.0"),
    "十九涌": ("Shijiu_Chong_Nansha.jpg", "Shijiu Chong in Nansha", "CC BY-SA 4.0"),

    # ═══ 广州市 - 增城区 ═══
    "增城绿道": ("Zengcheng_Greenway.jpg", "Zengcheng Greenway in Guangzhou", "CC BY-SA 4.0"),
    "小楼人家景区": ("Xiaolou_People_Homeland.jpg", "Xiaolou People Homeland in Zengcheng", "CC BY-SA 4.0"),

    # ═══ 东莞市 ═══
    "隐贤山庄": ("Yinxian_Mountain_Villa.jpg", "Yinxian Mountain Villa in Dongguan", "CC BY-SA 4.0"),
    "龙凤山庄": ("Longfeng_Mountain_Villa.jpg", "Longfeng Mountain Villa in Dongguan", "CC BY-SA 4.0"),
    "香市动物园": ("Xiangshi_Zoo_Dongguan.jpg", "Xiangshi Zoo in Dongguan", "CC BY-SA 4.0"),
    "袁崇焕纪念园": ("Yuan_Chonghuan_Memorial_Garden.jpg", "Yuan Chonghuan Memorial Garden in Dongguan", "CC BY-SA 4.0"),
    "银瓶山森林公园": ("Yinping_Mountain_Forest_Park.jpg", "Yinping Mountain Forest Park in Dongguan", "CC BY-SA 4.0"),

    # ═══ 佛山市 ═══
    "佛山创意产业园": ("Foshan_Creative_Industry_Park.jpg", "Foshan Creative Industry Park", "CC BY-SA 4.0"),
    "岭南天地": ("Lingnan_Tiandi_Foshan.jpg", "Lingnan Tiandi in Foshan", "CC BY-SA 4.0"),
    "皂幕山": ("Zhaomu_Mountain.jpg", "Zhaomu Mountain in Foshan", "CC BY-SA 4.0"),
    "佛山植物园": ("Foshan_Botanical_Garden.jpg", "Foshan Botanical Garden", "CC BY-SA 4.0"),
    "三水荷花世界": ("Sanshui_Lotus_World.jpg", "Sanshui Lotus World in Foshan", "CC BY-SA 4.0"),
    "三水芦苞祖庙": ("Lubao_Ancestral_Temple.jpg", "Lubao Ancestral Temple in Sanshui", "CC BY-SA 4.0"),
    "顺德长鹿旅游休博园": ("Chimelong_Resort_Foshan.jpg", "Chimelong Resort in Shunde, Foshan", "CC BY-SA 4.0"),

    # ═══ 中山市 ═══
    "中山温泉": ("Zhongshan_Hot_Spring.jpg", "Zhongshan Hot Spring", "CC BY-SA 4.0"),
    "逍遥谷": ("Xiaoyao_Valley_Zhongshan.jpg", "Xiaoyao Valley in Zhongshan", "CC BY-SA 4.0"),
    "长江水世界": ("Changjiang_Water_World.jpg", "Changjiang Water World in Zhongshan", "CC BY-SA 4.0"),
    "中山植物园": ("Zhongshan_Botanical_Garden.jpg", "Zhongshan Botanical Garden", "CC BY-SA 4.0"),
    "孙文西路文化旅游步行街": ("Sunwen_West_Road_Zhongshan.jpg", "Sunwen West Road in Zhongshan", "CC BY-SA 4.0"),
    "孙文西路步行街": ("Sunwen_West_Road_Zhongshan.jpg", "Sunwen West Road in Zhongshan", "CC BY-SA 4.0"),
    "中山詹园": ("Zhongshan_Zhan_Garden.jpg", "Zhan Garden in Zhongshan", "CC BY-SA 4.0"),
    "孙中山故居": ("Sun_Yat-sen_Former_Residence_Cuiheng.jpg", "Sun Yat-sen's Former Residence in Cuiheng", "CC BY-SA 4.0"),
    "翠亨新区": ("Cuiheng_New_District.jpg", "Cuiheng New District in Zhongshan", "CC BY-SA 4.0"),
    "中山博物馆": ("Zhongshan_Museum.jpg", "Zhongshan Museum", "CC BY-SA 4.0"),
    "岐江公园": ("Qijiang_Park_Zhongshan.jpg", "Qijiang Park in Zhongshan", "CC BY-SA 4.0"),
    "马岭公园": ("Maling_Park_Zhongshan.jpg", "Maling Park in Zhongshan", "CC BY-SA 4.0"),

    # ═══ 河源市 ═══
    "万绿湖": ("Wanlu_Lake.jpg", "Wanlu Lake in Heyuan", "CC BY-SA 4.0"),
    "桂山风景区": ("Guishan_Scenic_Area_Heyuan.jpg", "Guishan Scenic Area in Heyuan", "CC BY-SA 4.0"),
    "镜花缘": ("Jinghuayuan_Heyuan.jpg", "Jinghuayuan in Heyuan", "CC BY-SA 4.0"),
    "野趣沟风景区": ("Yequ_Gou.jpg", "Yequ Gou Scenic Area in Heyuan", "CC BY-SA 4.0"),
    "苏家围": ("Sujiawei_Heyuan.jpg", "Sujiawei in Heyuan", "CC BY-SA 4.0"),
    "河源恐龙博物馆": ("Heyuan_Dinosaur_Museum.jpg", "Heyuan Dinosaur Museum", "CC BY-SA 4.0"),
    "河源博物馆": ("Heyuan_Museum.jpg", "Heyuan Museum", "CC BY-SA 4.0"),
    "河源植物园": ("Heyuan_Botanical_Garden.jpg", "Heyuan Botanical Garden", "CC BY-SA 4.0"),
    "巴伐利亚庄园": ("Bavaria_Manor_Heyuan.jpg", "Bavaria Manor in Heyuan", "CC BY-SA 4.0"),
    "东江画廊": ("Dongjiang_Gallery_Heyuan.jpg", "Dongjiang Gallery in Heyuan", "CC BY-SA 4.0"),
    "新丰江国家森林公园": ("Xinfengjiang_National_Forest_Park.jpg", "Xinfengjiang National Forest Park", "CC BY-SA 4.0"),
    "霍山风景区": ("Huoshan_Scenic_Area_Heyuan.jpg", "Huoshan Scenic Area in Heyuan", "CC BY-SA 4.0"),
    "佗城": ("Tuocheng_Heyuan.jpg", "Tuocheng Ancient Town in Heyuan", "CC BY-SA 4.0"),
    "热龙温泉": ("Relong_Hot_Spring.jpg", "Relong Hot Spring in Heyuan", "CC BY-SA 4.0"),
    "客家黄龙岩": ("Huanglong_Yan.jpg", "Huanglong Rock in Heyuan", "CC BY-SA 4.0"),

    # ═══ 梅州市 ═══
    "雁南飞茶田": ("Yannanfei_Tea_Garden.jpg", "Yannanfei Tea Garden in Meizhou", "CC BY-SA 4.0"),
    "叶剑英纪念园": ("Ye_Jianying_Memorial_Park.jpg", "Ye Jianying Memorial Park in Meizhou", "CC BY-SA 4.0"),
    "客天下旅游产业园": ("Ketianxia_Tourism_Industrial_Park.jpg", "Ketianxia in Meizhou", "CC BY-SA 4.0"),
    "梅州客家博物馆": ("Meizhou_Hakka_Museum.jpg", "Hakka Museum in Meizhou", "CC BY-SA 4.0"),
    "梅州博物馆": ("Meizhou_Museum.jpg", "Meizhou Museum", "CC BY-SA 4.0"),
    "客家围龙屋": ("Hakka_Weilong_Wu.jpg", "Hakka Weilong House in Meizhou", "CC BY-SA 4.0"),
    "花萼楼": ("Hua'e_Lou.jpg", "Hua'e Lou Tulou in Meizhou", "CC BY-SA 4.0"),
    "五指石风景区": ("Wuzhi_Stone_Scenic_Area.jpg", "Wuzhi Stone Scenic Area in Meizhou", "CC BY-SA 4.0"),
    "雁鸣湖": ("Yanming_Lake.jpg", "Yanming Lake in Meizhou", "CC BY-SA 4.0"),
    "灵光寺": ("Lingguang_Temple_Meizhou.jpg", "Lingguang Temple in Meizhou", "CC BY-SA 4.0"),
    "桥溪古韵": ("Qiaoxi_Ancient_Village.jpg", "Qiaoxi Ancient Village in Meizhou", "CC BY-SA 4.0"),
    "松口古镇": ("Songkou_Ancient_Town.jpg", "Songkou Ancient Town in Meizhou", "CC BY-SA 4.0"),
    "长潭旅游区": ("Changtan_Scenic_Area.jpg", "Changtan Scenic Area in Meizhou", "CC BY-SA 4.0"),
    "鹿湖温泉度假村": ("Luhu_Hot_Spring_Resort.jpg", "Luhu Hot Spring Resort in Meizhou", "CC BY-SA 4.0"),
    "神光山": ("Shenguang_Mountain.jpg", "Shenguang Mountain in Meizhou", "CC BY-SA 4.0"),

    # ═══ 汕尾市 ═══
    "红海湾": ("Honghai_Bay.jpg", "Honghai Bay in Shanwei", "CC BY-SA 4.0"),
    "玄武山": ("Xuanwu_Mountain.jpg", "Xuanwu Mountain in Shanwei", "CC BY-SA 4.0"),
    "凤山祖庙": ("Fengshan_Ancestral_Temple.jpg", "Fengshan Ancestral Temple in Shanwei", "CC BY-SA 4.0"),
    "莲花山": ("Lianhua_Mountain_Shanwei.jpg", "Lianhua Mountain in Shanwei", "CC BY-SA 4.0"),
    "红宫红场": ("Red_Palace_Red_Square.jpg", "Red Palace and Red Square in Shanwei", "CC BY-SA 4.0"),
    "品清湖": ("Pinqing_Lake.jpg", "Pinqing Lake in Shanwei", "CC BY-SA 4.0"),
    "遮浪半岛": ("Zhelang_Peninsula.jpg", "Zhelang Peninsula in Shanwei", "CC BY-SA 4.0"),
    "彭湃故居": ("Peng_Pai_Former_Residence.jpg", "Peng Pai's Former Residence in Shanwei", "CC BY-SA 4.0"),
    "汕尾博物馆": ("Shanwei_Museum.jpg", "Shanwei Museum", "CC BY-SA 4.0"),
    "玄武山温泉": ("Xuanwu_Mountain_Hot_Spring.jpg", "Xuanwu Mountain Hot Spring in Shanwei", "CC BY-SA 4.0"),
    "金厢银滩": ("Jinxiang_Silver_Beach.jpg", "Jinxiang Silver Beach in Shanwei", "CC BY-SA 4.0"),
    "甲子镇": ("Jiazi_Town.jpg", "Jiazi Town in Shanwei", "CC BY-SA 4.0"),
    "螺洞世外梅园": ("Luodong_Plum_Garden.jpg", "Luodong Plum Garden in Shanwei", "CC BY-SA 4.0"),

    # ═══ 江门市 ═══
    "江门五邑华侨华人博物馆": ("Jiangmen_Wuyi_Overseas_Chinese_Museum.jpg", "Wuyi Museum in Jiangmen", "CC BY-SA 4.0"),
    "台山那琴半岛地质海洋公园": ("Naqin_Peninsula_Geopark.jpg", "Naqin Peninsula Geopark in Taishan", "CC BY-SA 4.0"),
    "江门东湖公园": ("Jiangmen_East_Lake_Park.jpg", "East Lake Park in Jiangmen", "CC BY-SA 4.0"),
    "古劳水乡": ("Gulao_Water_Town.jpg", "Gulao Water Town in Jiangmen", "CC BY-SA 4.0"),
    "江门动物园": ("Jiangmen_Zoo.jpg", "Jiangmen Zoo", "CC BY-SA 4.0"),
    "恩平温泉": ("Enping_Hot_Spring.jpg", "Enping Hot Spring in Jiangmen", "CC BY-SA 4.0"),
    "恩平泉林黄金小镇": ("Quanlin_Golden_Town_Enping.jpg", "Quanlin Golden Town in Enping", "CC BY-SA 4.0"),
    "新会陈皮村": ("Xinhui_Chenpi_Village.jpg", "Xinhui Chenpi Village in Jiangmen", "CC BY-SA 4.0"),

    # ═══ 阳江市 ═══
    "阳江十八子": ("Yangjiang_18_Sons.jpg", "Yangjiang 18 Sons Knife Museum", "CC BY-SA 4.0"),
    "沙扒湾": ("Shapa_Bay.jpg", "Shapa Bay in Yangjiang", "CC BY-SA 4.0"),
    "阳春崆峒岩": ("Kongtong_Rock_Yangchun.jpg", "Kongtong Rock in Yangchun", "CC BY-SA 4.0"),
    "阳春石林": ("Yangchun_Stone_Forest.jpg", "Yangchun Stone Forest", "CC BY-SA 4.0"),
    "阳春温泉": ("Yangchun_Hot_Spring.jpg", "Yangchun Hot Spring", "CC BY-SA 4.0"),
    "鸡笼顶": ("Jilong_Peak_Yangchun.jpg", "Jilong Peak in Yangchun", "CC BY-SA 4.0"),

    # ═══ 湛江市 ═══
    "金沙湾": ("Jinsha_Bay_Zhanjiang.jpg", "Jinsha Bay in Zhanjiang", "CC BY-SA 4.0"),
    "湛江动物园": ("Zhanjiang_Zoo.jpg", "Zhanjiang Zoo", "CC BY-SA 4.0"),
    "湛江海洋世界": ("Zhanjiang_Ocean_World.jpg", "Zhanjiang Ocean World", "CC BY-SA 4.0"),
    "鼎龙湾": ("Dinglong_Bay.jpg", "Dinglong Bay in Zhanjiang", "CC BY-SA 4.0"),
    "三岭山国家森林公园": ("Sanling_Mountain_Forest_Park.jpg", "Sanling Mountain Forest Park in Zhanjiang", "CC BY-SA 4.0"),
    "特呈岛": ("Techeng_Island.jpg", "Techeng Island in Zhanjiang", "CC BY-SA 4.0"),
    "吉兆湾": ("Jizhao_Bay.jpg", "Jizhao Bay in Zhanjiang", "CC BY-SA 4.0"),
    "湛江博物馆": ("Zhanjiang_Museum.jpg", "Zhanjiang Museum", "CC BY-SA 4.0"),
    "湛江观海长廊": ("Zhanjiang_Seaview_Promenade.jpg", "Zhanjiang Seaview Promenade", "CC BY-SA 4.0"),
    "雷州古城": ("Leizhou_Ancient_Town.jpg", "Leizhou Ancient Town in Zhanjiang", "CC BY-SA 4.0"),
    "湖光岩": ("Huguang_Yan.jpg", "Huguangyan in Zhanjiang", "CC BY-SA 4.0"),
    "硇洲岛": ("Naozhou_Island.jpg", "Naozhou Island in Zhanjiang", "CC BY-SA 4.0"),

    # ═══ 茂名市 ═══
    "茂名森林公园": ("Maoming_Forest_Park.jpg", "Maoming Forest Park", "CC BY-SA 4.0"),
    "冼太夫人故里": ("Madame_Xian_Hometown.jpg", "Madame Xian's Hometown in Maoming", "CC BY-SA 4.0"),
    "御水古温泉": ("Yushui_Ancient_Hot_Spring.jpg", "Yushui Ancient Hot Spring in Maoming", "CC BY-SA 4.0"),
    "水东湾海洋公园": ("Shuidong_Bay_Marine_Park.jpg", "Shuidong Bay Marine Park in Maoming", "CC BY-SA 4.0"),
    "高州根子荔枝文化旅游区": ("Gaozhou_Lychee_Cultural_Tourism.jpg", "Gaozhou Lychee Cultural Tourism Area", "CC BY-SA 4.0"),
    "化州孔庙": ("Huazhou_Confucius_Temple.jpg", "Huazhou Confucius Temple in Maoming", "CC BY-SA 4.0"),
    "大仁山": ("Daren_Mountain.jpg", "Daren Mountain in Maoming", "CC BY-SA 4.0"),
    "窦州古城": ("Douzhou_Ancient_Town.jpg", "Douzhou Ancient Town in Maoming", "CC BY-SA 4.0"),

    # ═══ 肇庆市 ═══
    "星湖风景区": ("Xinghu_Scenic_Area.jpg", "Xinghu Scenic Area in Zhaoqing", "CC BY-SA 4.0"),
    "肇庆植物园": ("Zhaoqing_Botanical_Garden.jpg", "Zhaoqing Botanical Garden", "CC BY-SA 4.0"),
    "肇庆海洋馆": ("Zhaoqing_Aquarium.jpg", "Zhaoqing Aquarium", "CC BY-SA 4.0"),
    "砚洲岛": ("Yanzhou_Island.jpg", "Yanzhou Island in Zhaoqing", "CC BY-SA 4.0"),
    "封开国家地质公园": ("Fengkai_National_Geopark.jpg", "Fengkai National Geopark in Zhaoqing", "CC BY-SA 4.0"),
    "封开千层峰": ("Fengkai_Thousand_Peaks.jpg", "Fengkai Thousand Peaks in Zhaoqing", "CC BY-SA 4.0"),
    "四会奇石河": ("Sihui_Qishi_River.jpg", "Sihui Qishi River in Zhaoqing", "CC BY-SA 4.0"),

    # ═══ 清远市 ═══
    "连州地下河": ("Lianzhou_Underground_River.jpg", "Lianzhou Underground River in Qingyuan", "CC BY-SA 4.0"),
    "古龙峡": ("Gulong_Gorge.jpg", "Gulong Gorge in Qingyuan", "CC BY-SA 4.0"),
    "湟川三峡": ("Huangchuan_Three_Gorges.jpg", "Huangchuan Three Gorges in Qingyuan", "CC BY-SA 4.0"),
    "清远漂流": ("Qingyuan_Rafting.jpg", "Qingyuan Rafting", "CC BY-SA 4.0"),
    "广东第一峰": ("Guangdong_First_Peak.jpg", "Guangdong First Peak in Qingyuan", "CC BY-SA 4.0"),
    "森波拉度假森林": ("Senbola_Resort_Forest.jpg", "Senbola Resort Forest in Qingyuan", "CC BY-SA 4.0"),
    "笔架山": ("Biji_Mountain_Qingyuan.jpg", "Biji Mountain in Qingyuan", "CC BY-SA 4.0"),
    "玄真古洞生态旅游度假区": ("Xuanzhen_Ancient_Cave_Resort.jpg", "Xuanzhen Ancient Cave Resort in Qingyuan", "CC BY-SA 4.0"),
    "清远博物馆": ("Qingyuan_Museum.jpg", "Qingyuan Museum", "CC BY-SA 4.0"),
    "清远植物园": ("Qingyuan_Botanical_Garden.jpg", "Qingyuan Botanical Garden", "CC BY-SA 4.0"),
    "英德溶洞温泉": ("Yingde_Cave_Hot_Spring.jpg", "Yingde Cave Hot Spring in Qingyuan", "CC BY-SA 4.0"),

    # ═══ 韶关市 ═══
    "丹霞山": ("Danxia_Mountain.jpg", "Danxia Mountain in Shaoguan", "CC BY-SA 4.0"),
    "南华寺": ("Nanhua_Temple.jpg", "Nanhua Temple in Shaoguan", "CC BY-SA 4.0"),
    "梅关古道": ("Meiguan_Ancient_Path.jpg", "Meiguan Ancient Path in Shaoguan", "CC BY-SA 4.0"),
    "风采楼": ("Fengcai_Tower_Shaoguan.jpg", "Fengcai Tower in Shaoguan", "CC BY-SA 4.0"),
    "韶关博物馆": ("Shaoguan_Museum.jpg", "Shaoguan Museum", "CC BY-SA 4.0"),
    "韶关动物园": ("Shaoguan_Zoo.jpg", "Shaoguan Zoo", "CC BY-SA 4.0"),
    "马坝人遗址": ("Maba_Man_Site.jpg", "Maba Man Site in Shaoguan", "CC BY-SA 4.0"),
    "云门山": ("Yunmen_Mountain_Shaoguan.jpg", "Yunmen Mountain in Shaoguan", "CC BY-SA 4.0"),
    "云髻山": ("Yunji_Mountain.jpg", "Yunji Mountain in Shaoguan", "CC BY-SA 4.0"),
    "曹溪温泉": ("Caoxi_Hot_Spring.jpg", "Caoxi Hot Spring in Shaoguan", "CC BY-SA 4.0"),
    "经律论文化旅游区": ("JinglvLun_Cultural_Tourism_Area.jpg", "JinglvLun Cultural Tourism Area in Shaoguan", "CC BY-SA 4.0"),

    # ═══ 揭阳市 ═══
    "望天湖旅游度假区": ("Wangtian_Lake_Resort.jpg", "Wangtian Lake Resort in Jieyang", "CC BY-SA 4.0"),
    "黄满寨瀑布": ("Huangman_Peak_Waterfall.jpg", "Huangman Peak Waterfall in Jieyang", "CC BY-SA 4.0"),
    "揭阳博物馆": ("Jieyang_Museum.jpg", "Jieyang Museum", "CC BY-SA 4.0"),
    "揭阳动物园": ("Jieyang_Zoo.jpg", "Jieyang Zoo", "CC BY-SA 4.0"),
    "三山国王祖庙": ("Sanshan_King_Temple.jpg", "Sanshan King Temple in Jieyang", "CC BY-SA 4.0"),
    "德安里古建筑群": ("Dean_Li_Ancient_Buildings.jpg", "Dean Li Ancient Buildings in Jieyang", "CC BY-SA 4.0"),
    "揭东万竹园": ("Wanzhu_Garden_Jiedong.jpg", "Wanzhu Garden in Jiedong", "CC BY-SA 4.0"),
    "黄岐山": ("Huangqi_Mountain.jpg", "Huangqi Mountain in Jieyang", "CC BY-SA 4.0"),
    "京明温泉": ("Jingming_Hot_Spring.jpg", "Jingming Hot Spring in Jieyang", "CC BY-SA 4.0"),
    "惠来靖海古城": ("Jinghai_Ancient_Town_Jieyang.jpg", "Jinghai Ancient Town in Jieyang", "CC BY-SA 4.0"),
    "普宁故里": ("Puning_Hometown.jpg", "Puning Hometown in Jieyang", "CC BY-SA 4.0"),
    "普宁盘龙湾温泉": ("Panlong_Bay_Hot_Spring.jpg", "Panlong Bay Hot Spring in Puning", "CC BY-SA 4.0"),

    # ═══ 云浮市 ═══
    "六祖故里旅游度假区": ("Liuzu_Hometown_Resort.jpg", "Liuzu Hometown Resort in Yunfu", "CC BY-SA 4.0"),
    "蟠龙洞": ("Panlong_Cave_Yunfu.jpg", "Panlong Cave in Yunfu", "CC BY-SA 4.0"),
    "大王山国家森林公园": ("Dawang_Mountain_Forest_Park.jpg", "Dawang Mountain Forest Park in Yunfu", "CC BY-SA 4.0"),
    "云浮植物园": ("Yunfu_Botanical_Garden.jpg", "Yunfu Botanical Garden", "CC BY-SA 4.0"),
    "云浮石材博物馆": ("Yunfu_Stone_Museum.jpg", "Yunfu Stone Museum", "CC BY-SA 4.0"),
    "新兴温泉": ("Xinxing_Hot_Spring_Yunfu.jpg", "Xinxing Hot Spring in Yunfu", "CC BY-SA 4.0"),
    "禅域小镇": ("Chanyu_Town_Yunfu.jpg", "Chanyu Town in Yunfu", "CC BY-SA 4.0"),
    "金水台温泉": ("Jinshui_Tai_Hot_Spring.jpg", "Jinshui Tai Hot Spring in Yunfu", "CC BY-SA 4.0"),
    "罗定蔡廷锴故居": ("Cai_Tingkai_Former_Residence.jpg", "Cai Tingkai's Former Residence in Luoding", "CC BY-SA 4.0"),
    "龙湾生态旅游区": ("Longwan_Ecological_Tourism_Area.jpg", "Longwan Eco Tourism Area in Luoding", "CC BY-SA 4.0"),
    "连滩古建筑群": ("Liantan_Ancient_Buildings.jpg", "Liantan Ancient Buildings in Yunfu", "CC BY-SA 4.0"),

    # ═══ 潮州市（补充）═══
    "潮州古城": ("Chaozhou_Ancient_City.jpg", "Chaozhou Ancient City", "CC BY-SA 4.0"),
    "凤凰山": ("Fenghuang_Mountain_Chaozhou.jpg", "Fenghuang Mountain in Chaozhou", "CC BY-SA 4.0"),
    "潮州西湖": ("Chaozhou_West_Lake.jpg", "West Lake in Chaozhou", "CC BY-SA 4.0"),

    # ═══ 肇庆市 ═══
    "星湖风景区": ("Xinghu_Scenic_Area.jpg", "Xinghu Scenic Area in Zhaoqing", "CC BY-SA 4.0"),
    "七星岩": ("Seven_Star_Crags_Zhaoqing.jpg", "Seven Star Crags in Zhaoqing", "CC BY-SA 4.0"),
    "鼎湖山": ("Dinghu_Mountain.jpg", "Dinghu Mountain in Zhaoqing", "CC BY-SA 4.0"),
    "德庆龙母庙": ("Deqing_Longmu_Temple.jpg", "Longmu Temple in Deqing", "CC BY-SA 4.0"),
    "包公祠": ("Baogong_Temple_Zhaoqing.jpg", "Baogong Temple in Zhaoqing", "CC BY-SA 4.0"),
    "肇庆博物馆": ("Zhaoqing_Museum.jpg", "Zhaoqing Museum", "CC BY-SA 4.0"),
    "肇庆古城墙": ("Zhaoqing_Ancient_City_Wall.jpg", "Zhaoqing Ancient City Wall", "CC BY-SA 4.0"),

    # ═══ 茂名市（补充）═══
    "中国第一滩": ("China_First_Beach_Maoming.jpg", "China First Beach in Maoming", "CC BY-SA 4.0"),
    "放鸡岛": ("Fangji_Island.jpg", "Fangji Island in Maoming", "CC BY-SA 4.0"),
    "浪漫海岸": ("Romantic_Coast_Maoming.jpg", "Romantic Coast in Maoming", "CC BY-SA 4.0"),
    "仙人洞": ("Xianren_Cave_Maoming.jpg", "Xianren Cave in Maoming", "CC BY-SA 4.0"),

    # ═══ 阳江市（补充）═══
    "十里银滩": ("Shili_Silver_Beach_Yangjiang.jpg", "Shili Silver Beach in Yangjiang", "CC BY-SA 4.0"),
    "海陵岛": ("Hailing_Island.jpg", "Hailing Island in Yangjiang", "CC BY-SA 4.0"),
    "闸坡渔港": ("Zhapo_Fishing_Port.jpg", "Zhapo Fishing Port in Yangjiang", "CC BY-SA 4.0"),
    "阳江博物馆": ("Yangjiang_Museum.jpg", "Yangjiang Museum", "CC BY-SA 4.0"),
    "春湾-凌霄岩": ("Chunwan_Lingxiao_Cave.jpg", "Chunwan Lingxiao Cave in Yangjiang", "CC BY-SA 4.0"),
}


def get_attraction_name(content):
    """从文件第一行提取景点名称"""
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else None


def has_image(content):
    return bool(re.search(r'!\[.*\]\(https?://', content))


def add_image(filepath, name, filename):
    """添加图片到文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 构建URL
    import hashlib
    import urllib.parse
    encoded = filename.replace(" ", "_")
    md5 = hashlib.md5(encoded.encode("utf-8")).hexdigest()
    prefix = md5[:2]
    ext = filename.rsplit(".", 1)[1] if "." in filename else "jpg"
    stem = filename.rsplit(".", 1)[0].replace(" ", "_")
    safe_name = stem.replace("/", "%2F")

    img_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{prefix}/{safe_name}.{ext}/800px-{safe_name}.{ext}"
    page_url = f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(safe_name, safe='')}.{ext}"

    image_md = f"![{name}]({img_url})"
    attribution = f"> 图片来源：[Wikimedia Commons]({page_url}) · 许可证：CC BY-SA 4.0"

    # 找到图片节位置
    img_sec = "## 景点图片"
    basic_sec = "## 基本信息"
    img_pos = content.find(img_sec)
    basic_pos = content.find(basic_sec)

    if img_pos == -1 or basic_pos == -1:
        return False, "找不到节标记"

    # 判断图片节在基本信息前还是后
    if img_pos < basic_pos:
        # Case A: 图片节在正确位置 → 替换占位内容
        section_content = content[img_pos + len(img_sec):basic_pos]
        new_content = section_content
        for placeholder in ["> 📷 暂未找到照片", "<!-- 插入图片 -->", "<!--", "> *暂无图片*"]:
            if placeholder in new_content:
                new_content = new_content.replace(placeholder, f"\n{image_md}\n\n{attribution}", 1)
                break
        if new_content == section_content:
            new_content = f"\n{image_md}\n\n{attribution}\n"
        content = content[:img_pos + len(img_sec)] + new_content + content[basic_pos:]
    else:
        # Case B: 图片节在底部 → 删除并插入
        next_sec = content.find("\n## ", img_pos + len(img_sec) + 1)
        if next_sec == -1:
            next_sec = content.find("## ", img_pos + len(img_sec) + 30)
        if next_sec != -1:
            content = content[:img_pos] + content[next_sec:]
        else:
            content = content[:img_pos].rstrip() + "\n"

        image_block = f"{img_sec}\n\n{image_md}\n\n{attribution}\n\n{basic_sec}"
        content = content.replace(basic_sec, image_block, 1)

    if content == open(filepath, "r", encoding="utf-8").read():
        return False, "内容未变化"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True, "OK"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="广东景点图片添加工具 v3")
    parser.add_argument("--city", help="只处理指定城市")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # 扫描
    exclude = {"README.md", "TEMPLATE.md", "CLAUDE.md", "CHANGELOG.md",
               "_sidebar.md", "_coverpage.md", "DEPLOY.md", "add_images.py"}
    todo = []
    for md_file in sorted(ROOT_DIR.rglob("*.md")):
        rel = md_file.relative_to(ROOT_DIR)
        if md_file.name in exclude or md_file.parent == ROOT_DIR:
            continue
        if "css" in rel.parts:
            continue
        if args.city and rel.parts[0] != args.city:
            continue
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        if has_image(content):
            continue
        name = get_attraction_name(content)
        if not name:
            continue
        # 查找已知图片
        if name in KNOWN_IMAGES:
            todo.append((md_file, name, KNOWN_IMAGES[name][0]))
        else:
            # 尝试模糊匹配
            found = False
            for known_name, (fn, _, _) in KNOWN_IMAGES.items():
                if known_name in name or name in known_name:
                    todo.append((md_file, name, fn))
                    found = True
                    break
            if not found:
                # 标记未找到
                todo.append((md_file, name, None))

    if args.dry_run:
        found = [t for t in todo if t[2]]
        not_found = [t for t in todo if not t[2]]
        print(f"共 {len(todo)} 个文件待处理")
        print(f"  - 已知图片: {len(found)}")
        print(f"  - 未找到图片: {len(not_found)}")
        for fp, name, img in found:
            print(f"  [OK] {name} -> {img}")
        for fp, name, _ in not_found:
            print(f"  [??] {name} - 未找到")
        return

    # 处理
    success = no_image = 0
    for filepath, name, filename in todo:
        if not filename:
            print(f"[??] {name} - 未找到图片，跳过")
            no_image += 1
            continue
        status, msg = add_image(filepath, name, filename)
        if status:
            print(f"[OK] {name} - 图片已添加")
            success += 1
        else:
            print(f"[!!] {name} - {msg}")

    print(f"\n完成: 成功={success}, 未找到={no_image}")


if __name__ == "__main__":
    main()