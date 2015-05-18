# encoding=utf-8
import werobot
from common import mongocli
from common import log
import configmgr
from datetime import datetime
from datetime import timedelta
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class WXRobotHandler():
    def __init__(self):
        # 初始化配置文件
        cfg = configmgr.RobotConfig()
        # 初始化mongo客户端
        self.mongo = mongocli.PyMongoHandler(cfg.mongo_host, cfg.mongo_port, cfg.mongo_db, cfg.mongo_user, cfg.mongo_passwd)
        self.mongo.connect_table(cfg.mongo_auction)
        # 初始化werobot客户端
        self.robot = werobot.WeRoBot(token=cfg.token, enable_session=True)
        self.curr_name = ''


        @self.robot.text
        def auction(message, session):
            '''
            竞拍接口，接收用户发来的p+价格，返回目前最高报价
            '''
            openid = message.source
            reply = None
            keyword = message.content[0]
#********************************************************************************
            if keyword == 's' and openid == 'this_is_openid_of_admin':
                log.INFO('[openid: %s] %s' % (openid, message.content))
                self.curr_name = message.content[1:]
                if self.mongo.table_find_one({'openid':'0000'}):
                    self.mongo.table_update({'openid': '0000'},{'finished': False, 'update_time': datetime.now()})
                else:
                    self.mongo.table_insert({'openid': '0000', 'finished': False, 'update_time': datetime.now()})
                reply = '拍卖系统启动!'
#********************************************************************************
            if keyword == 'r' and openid == 'this_is_openid_of_admin':
                self.mongo.table_update({'price': {'$ne': 0}},{'price': 0})
                reply = '拍卖系统重置完毕!'
#********************************************************************************
            if keyword == 'c' and openid == 'this_is_openid_of_admin':
                log.INFO('[openid: %s] %s' % (openid, message.content))
                self.mongo.table_update({'openid': '0000'},{'finished': True, 'finish_time': datetime.now()+timedelta(seconds=120), 'update_time': datetime.now()})
                reply = '拍卖系统关闭倒计时120秒启动……'
#********************************************************************************
            if keyword == 'p' or keyword == 'P':
                log.INFO('[openid: %s] %s' % (openid, message.content))
                mark = self.mongo.table_find_one({'openid': '0000'})
                if mark['finished']:
                    finish_time = mark['finish_time']
                    if int((finish_time - datetime.now()).days) < 0:
                        reply = '对不起，拍卖系统已关闭!\n\n请回复“t”查看最高出价'
                        return reply

                price = message.content[1:]
                if price.isdigit():
                    if int(price) <= 0:
                        reply = '您输入的金额无效！请重新输入\n\n回复“拍卖”可查看具体操作'
                        return reply

                    t = self.mongo.table_find_one({'openid': openid})
                    if t:
                        if t['price'] >= int(price):
                            reply = '对不起，您的竞价必须高于您上一次出价，请谨慎出价。\n\n回复“拍卖”可查看具体操作'
                            return reply

                        if t.has_key('contact'):
                            self.mongo.table_update({'openid': openid},{'price': int(price), 'update_time': datetime.now()})
                            reply = '新报价已录入！\n\n请回复“t”查看目前最高出价'
                        else:
                            self.mongo.table_insert({'openid':openid, 'price':int(price), 'update_time':datetime.now(), 'create_time':datetime.now()})
                            reply = '新报价已录入！\n请尽快回复“@+手机号码”完善联系方式，无联系方式竞价无效！\n'
                    else:
                        self.mongo.table_insert({'openid':openid, 'price':int(price), 'update_time':datetime.now(), 'create_time':datetime.now()})
                        reply = '新报价已录入！\n请尽快回复“@+手机号码”完善联系方式，无联系方式竞价无效！\n'

                    if mark['finished']:
                        self.mongo.table_update({'openid': '0000'},{'finish_time': datetime.now()+timedelta(seconds=120), 'update_time': datetime.now()})
                else:
                    reply = '对不起！请输入“p+金额数字”(如 p5， 代表您竞拍价格为5元)'

#********************************************************************************
            elif keyword == 't' or keyword == 'T':
                log.INFO('[openid: %s] %s' % (openid, message.content))
                mark = self.mongo.table_find_one({'openid': '0000'})
                max_players = self.mongo.get_max_players()
                if max_players:
                    reply = self.curr_name+'\n'
                    for i in range(0,len(max_players)):
                        reply += '【第%d名】%s元\n出价者：********%s\n' % (i+1, max_players[i]['price'], max_players[i]['contact'][-3:])

                    if mark['finished']:
                        finish_time = mark['finish_time']
                        if int((finish_time - datetime.now()).days) < 0:
                            reply += '\n拍卖系统已关闭!\n活动时间每周三/四/五晚9:00-9:30\n发布拍品可发邮件给sundayhs@qq.com'
                            return reply
                        else:
                            reply += '\n若无人出价，拍卖系统将在%s秒后关闭！\n' % ((finish_time - datetime.now()).seconds)

                    reply += '\n回复“p+金额”继续竞拍（如p5，代表您拍5元）'
                    reply += '\n回复“t”重新查询目前最高出价'
                else:
                    reply = self.curr_name+'\n'
                    if mark['finished']:
                        finish_time = mark['finish_time']
                        if int((finish_time - datetime.now()).days) < 0:
                            reply += '\n拍卖系统已关闭!\n活动时间每周三/四/五晚9:00-9:30\n发布拍品可发邮件给sundayhs@qq.com'
                            return reply
                    reply = '还没有人出价，快抓住机会！\n\n请回复“p+金额”参与竞拍（如p5，代表您拍5元）'

#********************************************************************************
            elif keyword == '@':
                log.INFO('[openid: %s] %s' % (openid, message.content))
                contact = message.content[1:]
                if contact.isdigit():
                    if len(contact) != 11:
                        reply = '对不起，请输入正确的手机号码!（如@13943214321）'
                        return reply

                    t = self.mongo.table_find_one({'openid': openid})
                    if t:
                        self.mongo.table_update({'openid':openid},{'contact': contact, 'update_time': datetime.now()})
                        reply = '联系方式修改成功!\n\n请回复“t”查看目前最高出价'
                    else:
                        self.mongo.table_update({'openid':openid},{'contact': contact, 'update_time': datetime.now()})
                        reply = '联系方式修改成功!\n\n请回复“t”查看目前最高出价'
                else:
                    reply = '对不起，请输入正确的手机号码!（如@13943214321）'
#********************************************************************************
            if reply is None:
                reply = '*请回复“拍卖”查询拍卖详情*'

            return reply

    def run(self):
        self.robot.run()


if __name__ == '__main__':
    handle = WXRobotHandler()
    handle.run()
