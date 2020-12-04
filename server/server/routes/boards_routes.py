# -*- coding: utf-8 -*-
"""
This file defines routes for board related API
"""
from flask import Blueprint, request, current_app

from server.config import Config
import server.routes.route_utils as route_utils
from server.routes.route_utils import cors_wrapped_route
from server.exceptions import MyAppException
from server.entity import Board

routes = Blueprint('boardRoutes', __name__)


@cors_wrapped_route(routes.route, '/v1/boards', methods=['GET'])
def searchBoardsv1():
    try:
        search = Config.getSearchService(current_app)
        result = search.searchBoardsByKeyValues( request.args.to_dict(flat=True) )
        result['boards'] = [ board.to_serialize() for board in result['boards'] ]
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)
