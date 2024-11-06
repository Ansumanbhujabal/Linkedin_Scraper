import redis
redis_host="localhost"
redis_port=6379
r=redis.StrictRedis(host=redis_host,port=redis_port,decode_responses=True)

def push_to_queue(key,value):
    try:
        r.set(key,value)
    except Exception as e:
        print(f"Something Wrong Happened :{e}") 
def pull_from_queue(key):
    try:
        result=r.get(key)
        print(result)
    except Exception as e:
        print(f"Something Wrong Happened :{e}")          

if __name__=="__main__":
    push_to_queue("Hello","World")
    pull_from_queue("Hello")