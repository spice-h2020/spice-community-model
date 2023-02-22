const Perspectives = require('../../service/PerspectivesService.js');
const Communities = require('../../service/CommunitiesService');
const CommunitiesVis = require('../../service/CommunitiesVisualizationService.js');

/**
 * Get specified promises that return requested data.
 * @param {string} request request type
 * @param {string} param parameters
 * @returns requested data
 */
export function getData(request, param) {
    switch (request) {
        case "getPerspectives":
            return Perspectives.getPerspectives();
            break;
        case "getPerspectiveById":
            return Perspectives.getPerspectiveById(param);
            break;
        case "listPerspectiveCommunities":
            return Perspectives.listPerspectiveCommunities(param);
            break;
        case "getCommunities":
            return Communities.getCommunities();
            break;
        case "getCommunityById":
            return Communities.getCommunityById(param);
            break;
        case "listCommunityUsers":
            return Communities.listCommunityUsers(param);
            break;
        case "getFilesIndex":
            return CommunitiesVis.getIndex();
            break;
        case "getFileById":
            return CommunitiesVis.getById(param);
            break;
        case "error":
            return new Promise(function (resolve) { resolve(param)});
            break;
        default:
            return new Promise(function (resolve) { resolve("getData not defined")});
            break;
    }
}
