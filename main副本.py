
import requests

cookies = {
    'JSESSIONID': '0FC01CD7FBB4C3F3BD7098667863596D',
    'Hm_lvt_11c3f77be047ea95e3773e8f9eeb11e9': '1784545505',
    'HMACCOUNT': '4404D05825CFFCE7',
    'Hm_lpvt_11c3f77be047ea95e3773e8f9eeb11e9': '1784547036',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Content-Length': '0',
    # 'Cookie': 'JSESSIONID=0FC01CD7FBB4C3F3BD7098667863596D; Hm_lvt_11c3f77be047ea95e3773e8f9eeb11e9=1784545505; HMACCOUNT=4404D05825CFFCE7; Hm_lpvt_11c3f77be047ea95e3773e8f9eeb11e9=1784547036',
    'Origin': 'https://120.35.29.78',
    'Pragma': 'no-cache',
    'Referer': 'https://120.35.29.78/eap/credit.showProjectInfo',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

params = {
    'type': 'getSlideCaptcha',
}

response = requests.post('https://120.35.29.78/eap/credit.vcodecheck', params=params, cookies=cookies, headers=headers)



params = {
    'type': 'slideValid',
    'imageToken': 'captcha_9ca4eb2b-9a5b-47e5-b850-509b0533f4c4',
}

data = {
    'trajectoryData': 'JEfFyX8PSkxs1wgPI2qGKYVEkm++cj/lJzVng+5VKw0hEIDyTbWYuGsBlB2ijYaTvjcfRhOWlLiAINgBwOF0QNUe1L77mIJ1xGHdz1gGvBH03r6ZuYbD45CpRvnA5khfmUVvfrdcwY0k3hL0LQUZM5tAKAxxt0Bm3dHberCU1UnoCSxi2JDKCyG3d+NNxZorDfj4Vi7p8E0U9jnYQ85L7XQgqcAescSyl8B2Zt0JWKHlnb5Hxs/waD7Yad6p+CTlpMSbYx9s9F6DPxjEosonVrzDZqnEEr72591J6A7gUYBREhV2NqrbER95tAcnsndsrgwCfoM4g3Jwat9Ofyanvw==|hECEftDTW6SvMnSMLirhBhA/fCRqULOLUYtKyxKozvwoUgqW+YtWPwirnn60seIpM4C+tHQKNHF6zpz40tUdwLR2Aq3cPkEj/w14qS88K6l/qyc0DgaJ8ZdwL00VB+5aR6OMESPTM9ehbgqV/BfB5nKkgcXpPidL/P2i9T2G1RoOtN7SuzP9qWD2auoHbxymEiOlXo9SlM4CC+oj+nNsW0QF7C0Im28K4PVClXJjgUQ08NybiGsFm7oEbXf7biu0TLpzMstY/+EFINfFBGpl3loPBcKdwDF4rLGydXwzogHlKKdo3zbGkzbZthJ+qyeQFNZd6713WorBmce1Z7XLOQ==|dRzJtGt3Kd2X4mjwuX0MtNY7iCxILilsQPEDEclX1/VrNg0Ce32a5vFdqWg3IMznifmsJg0LuWgj4nzLsQF5ZvXsYnNd0CgLlU6VGBSfQsstw9fT9g03Ds1mL3KWJtV9IMKuwnw2A6INU3N1pCp+PGsS8tLu09VwwxWOAE7AbKETVbwtOEyiAS2/J4P/QPiaUAhMBCrhYF7hUIU5tacxueq7eKo/LIrwGh2KGr4mFiUyir1RyYA02KkE2ej1C5v6jHygybLD0DNMfcdGPuBkuZurshjr8sAzhCDjFoMU9vtdVUivXPJzmk98qy3ip5dxiReTffPP7N66qepQVuHaaA==|GtuEhXjWBh2lw0+iWGGrfhOjwpWF/J8sQhsI+EU3GzGj7wB3YoFMiejN1E7QULbevQDb59SVbICN6FsD0/EK4ALxe5xeU44IfGtdDqEqYOejhFFMs6dHhCud/gD61guGl8OusyshN77xFVDeakvcTNjJWYiT0vnAPhJZhC9YWJmN70dn2nCKArYGRECrz1hH+OU6Dp7uKZVuEnlbte3NRS4ZOoQPRVn87ZBbQQDmhEwiovbVPMaUMjPhLn+pq6aScMV3Ihb7Sv+3urQkfoJTtTFx+b/kZr+/mcRGr05H2GR7VooPnDooham13RvhAeKF5o7WBrw+4m4gghkU2bbN1w==|WzFHvL+itq6N/2XMLY7qQuIMgJzoeezEXI1Sg2rcYktgLL6GGdGHDtRvQ4OaT/WOgOpiEFDbIlgJDOWc4GqUMZZMFjcxh9jbyizrNzc823dTy0+vnqdmCwsKqL9v2KovZSHOTmtQ0y/ZK/O3nXpR4bC9AiLjuv8dxrsE+RuPyrv48+BrMlh6Mzgj5Wq4W2xxsnjdEzRmZLzFUKL4kvL0yZndsG7ccmOsw4lpV1RTlbN0s19A5CXZEVbBuyPf6UKxnEGwKqqag/ZPAehHuiJ18ZaQ767Kvd9kzUiUm3TlsNLHb+ydHc5J04hP2C6nIzt1H6dYJQ2jqUnZw6vZHgfN1g==|SxRytLsSvboDJIjb57eiC1MAnoNvxKegiy3EkaQqBgNBAOMwRv0yoLlBD0tua2/VPrmXGaJAd69ii2Qs9uBYXc4Gz6F6CIyZqwm00yZlW0IbfdcuALcRs0FelwNvbjDtsOMTBD1Yd6E2qDHrxuciWqtlTFw0CtETemvjorFN9UZroyr2E0Jmk2cs2i/DgBBXvtFzoauq+J0f/CHytDEE+njUFmSFmF+z+Rv6suXfWYty+V2ogs5wifcnWP7XXNasXaTmaEP6q9d8V5axel9ZA/1nMyekMLm/RgCDHHqlr/Wo/7WFz9rr6kcxP8mvsPTSR5e1Ch+tC5WN/xI/otJLsQ==|RK28po6D0VBleVv3d4V9oyynHRJUkgpBcXXnTvWop0SI2HVmVEcy+zm6fqF7QsY/BT4O+GkCHqWxnAY/8DNKs5S/wnx5lQJsUXjn91VH+1zH01kaT8RMD149/drniFcuYl4xrQfJCljdRgdQImStq2QcAdE/zspbVzcivuE5PbUac9n9UYh71sQwIFeBhWvU84/gewdF868qsNplEwLx2ak0+ObCcNpUjaqT23W5/irjB9rVW6NXliaDhXW0YvXP7p/tO8KcMpjitld0hodiYbTCuhVf8aoUc1+TXMlB9Oksj+yQxDPB415EaSGGSdOnBSRfgjxi5FEUNwALY1gdxw==|DJitZN3nPygb8T0gxpxouDmSCETcUWiqEhaY7mKMWFeYgAUpALXr2LV5CqV7w5+Ip5a8ieneuL4MDrmLpvbgaPfZ+lJ1WyyBfrCJOotk6Kjuf3kQx11VdNFt1J0C1coG6RDT2qPiLGjMz4PYrP7q5qnfqWNp6WTSPpCD/z5jw3OWCc4lcS0QPKaoRDbF1B67przSBss/lQNVLxUo3O3/wBbfjkOlU/0sOZc+pJQSSb6o1zXNv+GIy+0pLnNNPBVrXVf9fIgrV1d5kNS58EuZQbKUnT3YcCDfoFhAcTkzYROS5PsMVukcviA0IeCYHs3Nh7GUKLC59n3aJl9SV8iScw==|I/G4h+3HR3x+qtXTANYcMLbPtHEEeqL/7qd6G0LoNoh0svnitFQaP3B5Ycv2cJAxSlrsvBR9RECGE4bsDu1gvktXmBN/JGYATaspMB6jVNGcWDoGFW5c5lnfX7ZiPRNhkPjD/chBk82w7xQoO0a1wxixtmslpk/L3Bak+HadbS3ThM3rqs3oU5F00gFEAg9V259zIKugSIRrJZnc76cqWoNxXK7Y2NBOJQ4ryoZ1+Yd3yL2c6ASKUwv6OyQF5XMp54CGYPa6ut5D8HhVey1U2Km7SnYGY8mDel/Nb3gk6m+cPO3AbsGW9aFIoWkXoJk//7mZlaTErPlsXIHJEemedg==|fTahEt6R371Rsd28c2v1udH5tZuraPf993SnTSU/bEraRqKUNPXMF90NEZLFqirSD8InHU7tEfRplNOKr/u6edazLJGH4cgpooEDfdmXvJWgXt79IYDh7R4KDYFui6FLHZT9c2uXITEnTbMab4T5zs+w3xlUMnf6OQvW3wXUsbMtCulFIH8jt6c2ZnEPwJWWShBEjfusVTagoXaOeWFPodj7Y1gaEiO8BGnSYzbnl1owiTaBXzXV50EGNL3X11Hs7s7j8PPrw7yHnXPmBHva2ZiD2sb7WXpAIyop3gIH6nh3Rzb4U8IDrJnsjWTGmTksoOSeQfOQzGp2UL2oUm8+BQ==|PWetled2WovioiCeK6/FxFxcKqpkbBS/1HweHPzB0dvXoqMOji/Jb3OSWWmGpd6UqjAcR8nA1x576EmT8jxZnXEHMamuRfMfPjVOu7BTNXYWx7bgH7OwDD45RnWQZn5iZCYikFWsDqagLtL2h1QHrfJ5Ra95T4bhQMoLwh2j6CeWqyAZVoBYrmkdibOJ8oOhIAuDGSbSlYUEh6d99lXs7uRmUaCoC4zS7eejbVcFEhGgsAW8F2HmHwcIeo6GGdFohDiS2yT3vvSXMiv4rcRQCiLZeGVJaCN/4enw5tvIPTX0FfDqyPaWIRodwC35PoBlkgguyVGi3YjGLkCd0D4UwA==|mMxIFEVOrqHRc2b4oPb0tLuRLMmjF5qTbOC6KgH1LyS2EjHjuAmY9cdIIYO4IIknUKeajyKxpHGDoNrv7JXetclneUDTfmmmwKXv43GsO1MFGEYuSjg5VQ1UL3GMpim8LvuWk1cS86wAbiz8XPxzoxE1EkcMKEHBk8SQhGENOtyw0QTTZtPA5UPz/OcjvnZLa+ocUhwuXqMkslkMRifeLuUzqb0PeJsEZtVR3dKUk7ZtJbFcAvbY4n375b1o2he/KJy3DwZrV8ow7ItzrNAPAV9GocEFLJqBwmFq5vKwTie+8mjUjFQfR59yjmm1zjCqdHR1KRnSTIyD+hjYE2b6bw==|eq6OXusjgmRVso/6tT+4rAf2Lvqp4oCGSId/7Z0EEVHJenCGnufs9ln+AaDQJVZIF93XJbJ50hpfdo595c4RNTSdcp4CtO99sivQr0SisKx0TcAXaCm15dXyqCnDO2+LOlBaQXAAabzDmVNBmwkFGINaefLW+XPfasuvHQySvUKfydNeCI6alSeFZDpmVrLTfKM++muymp82TSz3Q3wE2I3SZNHwgTSPDs4aMhgPvlLLnkZ/2bS7GI0Dz404wu7Hv6B+StsFhFREjzt+wids17p8g32TjTxr5UPBBI7FGhTM0Ef5wTfBBvMMpiXbDWz/9gih7tIAA1YYks8ik9lM2w==|gaHcI9B6fc0ljdQ7ofE8tJ4M7S8jotSiUhnsTmmOR7C198AzyYvj0dNyp69aPII9pLKavY84EzWs/Hvu/A1youWYy4/k8piupP5t+FfukMNi7jXOIia9ohcEjPD/EnaLlz5/qOnKUpfryN7C5zL4oSPt+rHYB1kJIBFy2yRDjW6VJK4tuxmGglGhJq6dCNhsT+neVGGoB2t6wbT24g2NkZyzemBq3P3lig/A7HhFSBpCcQdt52Oikf46HEf0Kk3AiAdszxfzNoUvYAXseRYYYVZPDyKi1zsazw64/nMHPSEKw2WzaU0Og/VgNKWhts4u+A54euCfShmL9QqZC7hKAQ==',
}

response = requests.post('https://120.35.29.78/eap/credit.vcodecheck', params=params, cookies=cookies, headers=headers, data=data)



data = {
    'page': '4',
    'project_name': '光伏',
    'project_code': '',
    'front_time': '2025-01-01',
    'behind_time': '2026-07-20',
    'project_type': '',
    'AreaName': '长泰区',
    'AreaCode': '350625',
    'is_in': '',
    'enterprise_name': '',
    'captchaToken': '0b55555ec7ea49518240e0d6ba3bb47d',
}

response = requests.post('https://120.35.29.78/eap/credit.showProjectInfo', cookies=cookies, headers=headers, data=data)
print(response.text)