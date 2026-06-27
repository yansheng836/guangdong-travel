export const meta = {
  name: 'download-guangzhou-images',
  description: '批量下载广州市景点图片到本地 images 目录',
  phases: [
    { title: '验证', detail: '并行检查 Wikimedia 原图 URL 是否可访问' },
    { title: '下载', detail: '下载可访问的图片到本地 images/' },
    { title: '更新', detail: '更新 md 文件引用为本地路径' },
  ],
}

// Derive original URL from thumbnail URL
function deriveOriginalUrl(thumbUrl) {
  if (thumbUrl.includes('/thumb/')) {
    const match = thumbUrl.match(/\/wikipedia\/commons\/thumb\/(\w\/\w\/[^/]+)\/\d+px-.+/)
    if (match) return 'https://upload.wikimedia.org/wikipedia/commons/' + match[1]
  }
  return thumbUrl
}

// All files with their thumbnail URLs
const files = [
  { path: '广州市-从化区-从化温泉风景区.md', name: '从化温泉风景区', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c0/Conghua_Hot_Spring.jpg/800px-Conghua_Hot_Spring.jpg' },
  { path: '广州市-从化区-碧水湾温泉度假区.md', name: '碧水湾温泉度假区', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a0/Bishui_Bay_Hot_Spring_Resort.jpg/800px-Bishui_Bay_Hot_Spring_Resort.jpg' },
  { path: '广州市-南沙区-十九涌.md', name: '十九涌', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d1/Shijiu_Chong_Nansha.jpg/800px-Shijiu_Chong_Nansha.jpg' },
  { path: '广州市-南沙区-南沙天后宫.md', name: '南沙天后宫', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/fb/Nansha_Tin_Hau_Temple.jpg/800px-Nansha_Tin_Hau_Temple.jpg' },
  { path: '广州市-南沙区-百万葵园.md', name: '百万葵园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/8/88/Sunflower_Garden.jpg' },
  { path: '广州市-南沙区-南沙湿地公园.md', name: '南沙湿地公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/a/a5/%E5%8D%97%E6%B2%99%E6%B9%BE%E5%9C%B0%E5%85%AC%E5%9B%ADScenery_in_Guangzhou%2C_China_-_panoramio_%281%29.jpg' },
  { path: '广州市-增城区-增城绿道.md', name: '增城绿道', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a2/Zengcheng_Greenway.jpg/800px-Zengcheng_Greenway.jpg' },
  { path: '广州市-增城区-小楼人家景区.md', name: '小楼人家景区', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/cb/Xiaolou_People_Homeland.jpg/800px-Xiaolou_People_Homeland.jpg' },
  { path: '广州市-增城区-白水寨.md', name: '白水寨风景名胜区', thumb: 'https://upload.wikimedia.org/wikipedia/commons/7/71/%E5%A2%9E%E5%9F%8E%E7%99%BD%E6%B0%B4%E5%AF%A8%E7%80%91%E5%B8%83%20-%20panoramio.jpg' },
  { path: '广州市-天河区-广州大剧院.md', name: '广州大剧院', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4d/Guangzhou_Opera_House.jpg/800px-Guangzhou_Opera_House.jpg' },
  { path: '广州市-天河区-正佳极地海洋世界.md', name: '正佳极地海洋世界', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d6/Zhengjia_Polar_Ocean_World.jpg/800px-Zhengjia_Polar_Ocean_World.jpg' },
  { path: '广州市-天河区-火炉山森林公园.md', name: '火炉山森林公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/43/Huolu_Mountain_Forest_Park.jpg/800px-Huolu_Mountain_Forest_Park.jpg' },
  { path: '广州市-天河区-红专厂创意艺术区.md', name: '红专厂创意艺术区', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2d/Redtory_Guangzhou.jpg/800px-Redtory_Guangzhou.jpg' },
  { path: '广州市-天河区-华南国家植物园.md', name: '华南国家植物园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/a/ab/South_China_Botanical_Garden_2009_1.jpg' },
  { path: '广州市-天河区-天河体育中心.md', name: '天河体育中心', thumb: 'https://upload.wikimedia.org/wikipedia/commons/1/1f/Tianhe_Stadium.jpg' },
  { path: '广州市-天河区-广东省博物馆.md', name: '广东省博物馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/7/7e/Guangdong_Museum.jpg' },
  { path: '广州市-天河区-广州图书馆.md', name: '广州图书馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Guangzhou_Library_20170915.jpg' },
  { path: '广州市-天河区-广州美术馆.md', name: '广州美术馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/d/d4/Aerial_View%2C_Guangzhou_Museum_of_Art_20241027-A.jpg' },
  { path: '广州市-天河区-花城广场.md', name: '花城广场', thumb: 'https://upload.wikimedia.org/wikipedia/commons/b/be/%E8%8A%B1%E5%9F%8E%E5%B9%BF%E5%9C%BA.jpg' },
  { path: '广州市-海珠区-TIT创意园.md', name: 'TIT创意园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e6/TIT_Creative_Park.jpg/800px-TIT_Creative_Park.jpg' },
  { path: '广州市-海珠区-中山大学南校园.md', name: '中山大学（南校园）', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/23/Sun_Yat-sen_University_Guangzhou.jpg/800px-Sun_Yat-sen_University_Guangzhou.jpg' },
  { path: '广州市-海珠区-十香园.md', name: '十香园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/26/Shixiang_Garden.jpg/800px-Shixiang_Garden.jpg' },
  { path: '广州市-海珠区-孙中山大元帅府纪念馆.md', name: '孙中山大元帅府纪念馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/49/Former_Residence_of_Sun_Yat-sen_Commander.jpg/800px-Former_Residence_of_Sun_Yat-sen_Commander.jpg' },
  { path: '广州市-海珠区-小洲村.md', name: '小洲村', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/cd/Xiaozhou_Village.jpg/800px-Xiaozhou_Village.jpg' },
  { path: '广州市-海珠区-广州市文化馆.md', name: '广州市文化馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/52/Guangzhou_Cultural_Center.jpg/800px-Guangzhou_Cultural_Center.jpg' },
  { path: '广州市-海珠区-广州艺术博物院.md', name: '广州艺术博物院', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/50/Guangzhou_Art_Museum.jpg/800px-Guangzhou_Art_Museum.jpg' },
  { path: '广州市-海珠区-海珠湖公园.md', name: '海珠湖公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/52/Haizhu_Lake_Park.jpg/800px-Haizhu_Lake_Park.jpg' },
  { path: '广州市-海珠区-海珠湿地公园.md', name: '海珠湿地公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/ff/Haizhu_Wetland_Park.jpg/800px-Haizhu_Wetland_Park.jpg' },
  { path: '广州市-海珠区-潘鹤雕塑艺术园.md', name: '潘鹤雕塑艺术园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d2/Pan_He_Sculpture_Park.jpg/800px-Pan_He_Sculpture_Park.jpg' },
  { path: '广州市-海珠区-珠江琶醍啤酒文化创意艺术区.md', name: '珠江·琶醍啤酒文化创意艺术区', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e4/Party_Pier_Guangzhou.jpg/800px-Party_Pier_Guangzhou.jpg' },
  { path: '广州市-海珠区-纯阳观.md', name: '纯阳观', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/72/Chunyang_Temple_Guangzhou.jpg/800px-Chunyang_Temple_Guangzhou.jpg' },
  { path: '广州市-海珠区-邓世昌纪念馆.md', name: '邓世昌纪念馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/92/Deng_Shichang_Memorial.jpg/800px-Deng_Shichang_Memorial.jpg' },
  { path: '广州市-海珠区-黄埔古港.md', name: '黄埔古港', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6b/Huangpu_Ancient_Port.jpg/800px-Huangpu_Ancient_Port.jpg' },
  { path: '广州市-海珠区-太古仓码头.md', name: '太古仓码头', thumb: 'https://upload.wikimedia.org/wikipedia/commons/0/0c/%E5%A4%AA%E5%8F%A4%E4%BB%93%E7%A0%81%E5%A4%B4_-_panoramio.jpg' },
  { path: '广州市-海珠区-广州塔.md', name: '广州塔', thumb: '', local: true },
  { path: '广州市-番禺区-余荫山房.md', name: '余荫山房', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0f/Yuyin_Mountain_House.jpg/800px-Yuyin_Mountain_House.jpg' },
  { path: '广州市-番禺区-南汉二陵博物馆.md', name: '南汉二陵博物馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e6/Nanhan_Two_Tombs_Museum.jpg/800px-Nanhan_Two_Tombs_Museum.jpg' },
  { path: '广州市-番禺区-大夫山森林公园.md', name: '大夫山森林公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b4/Dafu_Mountain_Forest_Park.jpg/800px-Dafu_Mountain_Forest_Park.jpg' },
  { path: '广州市-番禺区-宝墨园.md', name: '宝墨园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c2/Baomo_Garden.jpg/800px-Baomo_Garden.jpg' },
  { path: '广州市-番禺区-岭南印象园.md', name: '岭南印象园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d0/Lingnan_Impression_Park.jpg/800px-Lingnan_Impression_Park.jpg' },
  { path: '广州市-番禺区-广东科学中心.md', name: '广东科学中心', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9f/Guangdong_Science_Center.jpg/800px-Guangdong_Science_Center.jpg' },
  { path: '广州市-番禺区-沙湾古镇.md', name: '沙湾古镇', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/21/Shawan_Ancient_Town.jpg/800px-Shawan_Ancient_Town.jpg' },
  { path: '广州市-番禺区-紫泥堂创意园.md', name: '紫泥堂创意园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/30/Zinitang_Creative_Park.jpg/800px-Zinitang_Creative_Park.jpg' },
  { path: '广州市-番禺区-莲花山.md', name: '莲花山', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0c/Lianhua_Mountain_Shanwei.jpg/800px-Lianhua_Mountain_Shanwei.jpg' },
  { path: '广州市-番禺区-长隆欢乐世界.md', name: '长隆欢乐世界', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/ff/Chimelong_Paradise.jpg/800px-Chimelong_Paradise.jpg' },
  { path: '广州市-番禺区-长隆水上乐园.md', name: '长隆水上乐园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a2/Chimelong_Water_Park.jpg/800px-Chimelong_Water_Park.jpg' },
  { path: '广州市-番禺区-长隆野生动物世界.md', name: '长隆野生动物世界', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/ff/Chimelong_Safari_Park.jpg/800px-Chimelong_Safari_Park.jpg' },
  { path: '广州市-白云区-云台花园.md', name: '云台花园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/56/Yuntai_Garden.jpg/800px-Yuntai_Garden.jpg' },
  { path: '广州市-白云区-帽峰山.md', name: '帽峰山森林公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a1/Maofeng_Mountain.jpg/800px-Maofeng_Mountain.jpg' },
  { path: '广州市-白云区-白云山.md', name: '白云山', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/54/Baiyun_Mountain_Guangzhou.jpg/800px-Baiyun_Mountain_Guangzhou.jpg' },
  { path: '广州市-白云区-白云湖公园.md', name: '白云湖公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c7/Baiyun_Lake_Park.jpg/800px-Baiyun_Lake_Park.jpg' },
  { path: '广州市-花都区-九龙湖度假区.md', name: '九龙湖度假区', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/ce/Jiulong_Lake_Resort.jpg/800px-Jiulong_Lake_Resort.jpg' },
  { path: '广州市-花都区-花都湖.md', name: '花都湖', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/da/Huadu_Lake.jpg/800px-Huadu_Lake.jpg' },
  { path: '广州市-荔湾区-上下九步行街.md', name: '上下九步行街', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f9/Shangxiajiu_Pedestrian_Street.jpg/800px-Shangxiajiu_Pedestrian_Street.jpg' },
  { path: '广州市-荔湾区-华林寺.md', name: '华林寺', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/23/Hualin_Temple.jpg/800px-Hualin_Temple.jpg' },
  { path: '广州市-荔湾区-永庆坊.md', name: '永庆坊', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/83/Yongqing_Fang.jpg/800px-Yongqing_Fang.jpg' },
  { path: '广州市-荔湾区-沙面.md', name: '沙面', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/12/Shamian_Island.jpg/800px-Shamian_Island.jpg' },
  { path: '广州市-荔湾区-荔枝湾涌.md', name: '荔枝湾涌', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/99/Lizhi_Bay_Stream.jpg/800px-Lizhi_Bay_Stream.jpg' },
  { path: '广州市-荔湾区-荔湾湖公园.md', name: '荔湾湖公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/da/Liwan_Lake_Park.jpg/800px-Liwan_Lake_Park.jpg' },
  { path: '广州市-荔湾区-西关大屋.md', name: '西关大屋', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6a/Xiguan_Great_Houses.jpg/800px-Xiguan_Great_Houses.jpg' },
  { path: '广州市-荔湾区-陈家祠.md', name: '陈家祠', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6b/Chen_Clan_Ancestral_Hall.jpg/800px-Chen_Clan_Ancestral_Hall.jpg' },
  { path: '广州市-越秀区-三元宫.md', name: '三元宫', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/07/Sanyuan_Temple_Guangzhou.jpg/800px-Sanyuan_Temple_Guangzhou.jpg' },
  { path: '广州市-越秀区-中共三大会址纪念馆.md', name: '中共三大会址纪念馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f9/Third_CPC_Congress_Site.jpg/800px-Third_CPC_Congress_Site.jpg' },
  { path: '广州市-越秀区-中山纪念堂.md', name: '中山纪念堂', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/87/Sun_Yat-sen_Memorial_Hall.jpg/800px-Sun_Yat-sen_Memorial_Hall.jpg' },
  { path: '广州市-越秀区-二沙岛.md', name: '二沙岛', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/02/Ersha_Island.jpg/800px-Ersha_Island.jpg' },
  { path: '广州市-越秀区-光孝寺.md', name: '光孝寺', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/db/Guangxiao_Temple.jpg/800px-Guangxiao_Temple.jpg' },
  { path: '广州市-越秀区-六榕寺.md', name: '六榕寺', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e0/Liurong_Temple.jpg/800px-Liurong_Temple.jpg' },
  { path: '广州市-越秀区-农民运动讲习所旧址.md', name: '农民运动讲习所旧址', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/49/Peasant_Movement_Institute.jpg/800px-Peasant_Movement_Institute.jpg' },
  { path: '广州市-越秀区-北京路步行街.md', name: '北京路步行街', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/26/Beijing_Road_Guangzhou.jpg/800px-Beijing_Road_Guangzhou.jpg' },
  { path: '广州市-越秀区-广东美术馆.md', name: '广东美术馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d2/Guangdong_Museum_of_Art.jpg/800px-Guangdong_Museum_of_Art.jpg' },
  { path: '广州市-越秀区-广州动物园.md', name: '广州动物园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/57/Guangzhou_Zoo.jpg/800px-Guangzhou_Zoo.jpg' },
  { path: '广州市-越秀区-广州博物馆.md', name: '广州博物馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c4/Guangzhou_Museum.jpg/800px-Guangzhou_Museum.jpg' },
  { path: '广州市-越秀区-广州起义纪念馆.md', name: '广州起义纪念馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9e/Guangzhou_Uprising_Memorial.jpg/800px-Guangzhou_Uprising_Memorial.jpg' },
  { path: '广州市-越秀区-怀圣寺.md', name: '怀圣寺', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a1/Huaisheng_Mosque.jpg/800px-Huaisheng_Mosque.jpg' },
  { path: '广州市-越秀区-珠江夜游.md', name: '珠江夜游', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/47/Pearl_River_Night_Cruise.jpg/800px-Pearl_River_Night_Cruise.jpg' },
  { path: '广州市-越秀区-石室圣心大教堂.md', name: '石室圣心大教堂', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/ac/Sacred_Heart_Cathedral_Guangzhou.jpg/800px-Sacred_Heart_Cathedral_Guangzhou.jpg' },
  { path: '广州市-越秀区-西汉南越王博物馆.md', name: '西汉南越王博物馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/13/Nanyue_King_Museum.jpg/800px-Nanyue_King_Museum.jpg' },
  { path: '广州市-越秀区-越秀公园.md', name: '越秀公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9e/Yuexiu_Park_Guangzhou.jpg/800px-Yuexiu_Park_Guangzhou.jpg' },
  { path: '广州市-越秀区-黄花岗七十二烈士墓.md', name: '黄花岗七十二烈士墓', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/32/Mausoleum_of_72_Martyrs.jpg/800px-Mausoleum_of_72_Martyrs.jpg' },
  { path: '广州市-黄埔区-南海神庙.md', name: '南海神庙', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6d/Nanhai_Temple.jpg/800px-Nanhai_Temple.jpg' },
  { path: '广州市-黄埔区-天鹿湖森林公园.md', name: '天鹿湖森林公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c5/Tianlu_Lake_Forest_Park.jpg/800px-Tianlu_Lake_Forest_Park.jpg' },
  { path: '广州市-黄埔区-广州海事博物馆.md', name: '广州海事博物馆', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/90/Guangzhou_Maritime_Museum.jpg/800px-Guangzhou_Maritime_Museum.jpg' },
  { path: '广州市-黄埔区-长洲岛.md', name: '长洲岛', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/03/Changzhou_Island_Guangzhou.jpg/800px-Changzhou_Island_Guangzhou.jpg' },
  { path: '广州市-黄埔区-黄埔军校旧址.md', name: '黄埔军校旧址', thumb: 'https://upload.wikimedia.org/wikipedia/commons/thumb/51/Whampoa_Military_Academy.jpg/800px-Whampoa_Military_Academy.jpg' },
  { path: '广州市-从化区-流溪河国家森林公园.md', name: '流溪河国家森林公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/4/46/%E6%B5%81%E6%BA%AA%E9%A6%99%E9%9B%AAScenery_in_GhuangZhou%2C_China_-_panoramio_%284%29.jpg' },
  { path: '广州市-从化区-石门国家森林公园.md', name: '石门国家森林公园', thumb: 'https://upload.wikimedia.org/wikipedia/commons/9/9a/%E7%9F%B3%E9%97%A8%E5%9B%BD%E5%AE%B6%E6%A3%AE%E6%9E%97%E5%85%AC%E5%9B%ADScenery_in_GhuangZhou%2C_China_-_panoramio.jpg' },
]

phase('验证')

// Build URL list with derived original URLs
const urlList = files.filter(f => !f.local).map(f => ({
  ...f,
  originalUrl: deriveOriginalUrl(f.thumb),
  localName: f.path.replace('.md', ''),
}))

// Phase 1: validate all URLs
const validations = await parallel(urlList.slice(0, 10).map((u, i) => () =>
  agent(`验证 URL 可访问性: ${u.originalUrl}`, {
    label: `验证:${u.name}`,
    phase: '验证',
  })
))

const valid = []
const failed = []
for (let i = 0; i < validations.length; i++) {
  if (validations[i] && validations[i].includes('200')) {
    valid.push(urlList[i])
  } else {
    failed.push({ ...urlList[i], reason: validations[i] || 'unknown' })
  }
}

// Continue validating remaining URLs in batches
if (urlList.length > 10) {
  const remaining = urlList.slice(10)
  const batchSize = 10
  for (let start = 0; start < remaining.length; start += batchSize) {
    const batch = remaining.slice(start, start + batchSize)
    log(`验证批次 ${Math.floor(start/batchSize)+2}: ${batch.map(f => f.name).join(', ')}`)
    const batchResults = await parallel(batch.map(u => () =>
      agent(`验证 URL 可访问性: ${u.originalUrl}`, {
        label: `验证:${u.name}`,
        phase: '验证',
      })
    ))
    for (let j = 0; j < batchResults.length; j++) {
      if (batchResults[j] && batchResults[j].includes('200')) {
        valid.push(batch[j])
      } else {
        failed.push({ ...batch[j], reason: batchResults[j] || 'unknown' })
      }
    }
  }
}

log(`验证完成: ${valid.length} 个可下载, ${failed.length} 个失败`)

phase('下载')

// Download valid files in batches
const downloaded = []
if (valid.length > 0) {
  const batchSize = 10
  for (let start = 0; start < valid.length; start += batchSize) {
    const batch = valid.slice(start, start + batchSize)
    log(`下载批次 ${Math.floor(start/batchSize)+1}: ${batch.map(f => f.name).join(', ')}`)

    const downloads = await parallel(batch.map(u => () =>
      agent(`下载图片: ${u.originalUrl} 保存到 ${u.localName}.jpg`, {
        label: `下载:${u.name}`,
        phase: '下载',
      })
    ))

    for (let j = 0; j < downloads.length; j++) {
      if (downloads[j] && !downloads[j].includes('失败') && !downloads[j].includes('error')) {
        downloaded.push(batch[j])
      }
    }
  }
}

log(`下载完成: ${downloaded.length}/${valid.length} 个成功`)

phase('更新')
log(`准备更新 ${downloaded.length} 个 md 文件引用`)

return {
  total: files.length,
  valid: valid.length,
  failed: failed.length,
  downloaded: downloaded.length,
  failedDetails: failed.slice(0, 5).map(f => `${f.name}: ${f.reason}`),
}
