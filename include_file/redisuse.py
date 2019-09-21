from redis import StrictRedis


class RedisUse(object):
    def __init__(self):
        self.sr = StrictRedis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

    def insertTokenOpenid(self, token, openid):
        res = self.sr.set(token, openid)
        res_time = self.sr.expire(token, 7200)

        return res

    def getTokenOpenid(self, token):
        res = self.sr.get(token)

        return res

    def insertOpenidData(self, openid, data):
        res = self.sr.hmset(openid, data)
        res_time = self.sr.expire(openid, 604800)

        return res

    def selectOpenidNature(self, openid):
        res = self.sr.hkeys(openid)

        return res

    def getOpenidNature(self, openid, nature):
        res = self.sr.hget(openid, nature)

        return res

    def getOpenidNatureAll(self, openid):
        res = self.sr.hgetall(openid)

        return res

    def deleteOpenidNature(self, openid, keys):
        res = self.sr.hdel(openid, keys)

        return res
