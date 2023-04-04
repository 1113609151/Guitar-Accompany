# 开始计时，每计时1s中将总时长进行输出
import time
#开始计时
start_time = time.time()
while(1):
        time.sleep(1)
        print(f"总时长：{time.time() - start_time}")
                
