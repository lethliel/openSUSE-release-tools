from osc import oscerr
from osclib.request_finder import RequestFinder


class SelectCommand(object):

    def __init__(self, api):
        self.api = api

    def select_request(self, rq, rq_prj, move, from_):
        if 'staging' not in rq_prj:
            # Normal 'select' command
            return self.api.rq_to_prj(rq, self.tprj)
        elif 'staging' in rq_prj and move:
            # 'select' command becomes a 'move'
            fprj = None
            if from_:
                fprj = self.api.prj_from_letter(from_)
            else:
                fprj = rq_prj['staging']
            print('Moving "{}" from "{}" to "{}"'.format(rq, fprj, self.tprj))
            return self.api.move_between_project(fprj, rq, self.tprj)
        elif 'staging' in rq_prj and not move:
            # Previously selected, but not explicit move
            msg = 'Request {} is actually in "{}".\n'
            msg = msg.format(rq, rq_prj['staging'])
            msg += 'Use --move modifier to move the request from "{}" to "{}"'
            msg = msg.format(rq_prj['staging'], self.tprj)
            print(msg)
            return False
        else:
            raise oscerr.WrongArgs('Arguments for select are not correct.')

    def perform(self, tprj, requests, move=False, from_=None):
        if not self.api.prj_frozen_enough(tprj):
            print('Freeze the prj first')
            return False
        self.tprj = tprj

        for rq, rq_prj in RequestFinder.find_sr(requests, self.api.apiurl).items():
            if not self.select_request(rq, rq_prj, move, from_):
                return False

        # now make sure we enable the prj
        self.api.build_switch_prj(tprj, 'enable')
        return True
