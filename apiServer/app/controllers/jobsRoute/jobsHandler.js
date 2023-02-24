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
        case "getPerspectiveById":
            return Perspectives.getPerspectiveById(param);
        case "listPerspectiveCommunities":
            return Perspectives.listPerspectiveCommunities(param);
        case "getCommunities":
            return Communities.getCommunities();
        case "getCommunityById":
            return Communities.getCommunityById(param);
        case "listCommunityUsers":
            return Communities.listCommunityUsers(param);
        case "getFilesIndex":
            return CommunitiesVis.getIndex();
        case "getFileById":
            return CommunitiesVis.getById(param);
        case "error":
            return new Promise(function (resolve) {
                resolve(param)
            });
        default:
            return new Promise(function (resolve) {
                resolve("getData not defined")
            });
    }
}
