import tornado.ioloop
import tornado.web
import json

from mcpParamCurve import *
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    async def post(self):
        try:
            req = json.loads(self.request.body.decode('utf-8'))
            print('req is:' + str(req))
            ref_date=req['ref_date']
            curve_category=req['curve_category']
            mat_dates= req['mat_dates']
            print("req is: ref_date {0}, curve_category {1}, mat_dates {2},"
                  .format(ref_date, curve_category, str(mat_dates), ))
            #id = await self.service.create_address(addr)
            #addr_uri = ADDRESSBOOK_ENTRY_URI_FORMAT_STR.format(id=id)
            results = get_ylds(pd.to_datetime(ref_date),curve_category,pd.to_datetime(mat_dates))
            resp = {
                    "ref_date": ref_date,
                    "curve_category": curve_category,
                    "mat_dates": mat_dates,
                    "yeilds": results,
                    }
            self.set_status(201)
            #self.set_header('Location', addr_uri)
            self.finish(resp)
        except (json.decoder.JSONDecodeError, TypeError):
            raise tornado.web.HTTPError(
                400, reason='Invalid JSON body'
            )
        except ValueError as e:
            raise tornado.web.HTTPError(400, reason=str(e))

def make_app():
    return tornado.web.Application([
        (r"/curve", MainHandler),
    ])

if __name__ == "__main__":
    import sys
    import asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app = make_app()
    app.listen(8888)
    print('start----------ING')
    tornado.ioloop.IOLoop.current().start()
