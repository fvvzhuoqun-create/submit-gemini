package self.cases.teams.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;

import self.cases.teams.entity.Users;
import self.cases.teams.handle.CacheHandle;
import self.cases.teams.service.UsersService;
import self.cases.teams.utils.DateUtils;
import self.cases.teams.utils.IDUtils;
import self.cases.teams.msg.R;
import self.cases.teams.msg.PageData;

import self.cases.teams.entity.ApplyLogs;
import self.cases.teams.service.ApplyLogsService;

/**
 * 系统请求响应控制器
 * 申请记录
 */
@Controller
@RequestMapping("/applyLogs")
public class ApplyLogsController extends BaseController {

    protected static final Logger Log = LoggerFactory.getLogger(ApplyLogsController.class);

    @Autowired
    private CacheHandle cacheHandle;

    @Autowired
    private UsersService usersService;

    @Autowired
    private ApplyLogsService applyLogsService;

    @RequestMapping("")
    public String index() {

        return "pages/ApplyLogs";
    }

    @GetMapping("/info")
    @ResponseBody
    public R getInfo(String id) {

        Log.info("查找指定申请记录，ID：{}", id);

        ApplyLogs applyLogs = applyLogsService.getOne(id);

        return R.successData(applyLogs);
    }

    @GetMapping("/page")
    @ResponseBody
    public R getPageInfos(Long pageIndex, Long pageSize,
                          String token, String teamName, String userName) {

        Users user = usersService.getOne(cacheHandle.getUserInfoCache(token));

        if (user.getType() == 0) {

            Log.info("分页查看全部申请记录，当前页码：{}，"
                            + "每页数据量：{}, 模糊查询，团队名称：{}，用户姓名：{}", pageIndex,
                    pageSize, teamName, userName);

            PageData page = applyLogsService.getPageInfo(pageIndex, pageSize, null, teamName, userName);

            return R.successData(page);

        } else if (user.getType() == 1) {

            Log.info("团队管理员查看申请记录，当前页码：{}，"
                            + "每页数据量：{}, 模糊查询，团队名称：{}，用户姓名：{}", pageIndex,
                    pageSize, teamName, userName);

            PageData page = applyLogsService.getManPageInfo(pageIndex, pageSize, user.getId(), teamName, userName);

            return R.successData(page);

        } else {

            Log.info("分页用户相关申请记录，当前页码：{}，"
                            + "每页数据量：{}, 模糊查询，团队名称：{}，用户姓名：{}", pageIndex,
                    pageSize, teamName, userName);

            PageData page = applyLogsService.getPageInfo(pageIndex, pageSize, user.getId(), teamName, null);

            return R.successData(page);
        }
    }

    @PostMapping("/add")
    @ResponseBody
    public R addInfo(String token, ApplyLogs applyLogs) {

        Users user = usersService.getOne(cacheHandle.getUserInfoCache(token));

        // 调用新的检查逻辑
        String errorMsg = applyLogsService.checkApply(user.getId(), applyLogs.getTeamId());

        if(errorMsg == null){ // 检查通过

            applyLogs.setId(IDUtils.makeIDByCurrent());
            applyLogs.setUserId(user.getId());
            applyLogs.setCreateTime(DateUtils.getNowDate());
            applyLogs.setStatus(0); // 默认为待审核

            Log.info("添加申请记录，传入参数：{}", applyLogs);

            applyLogsService.add(applyLogs);

            return R.success();
        } else {
            // 返回具体的错误原因（已入团、审核中、冷静期未过）
            return R.warn(errorMsg);
        }
    }

    @PostMapping("/upd")
    @ResponseBody
    public R updInfo(ApplyLogs applyLogs) {

        Log.info("修改申请记录，传入参数：{}", applyLogs);

        applyLogsService.update(applyLogs);

        return R.success();
    }

    @PostMapping("/del")
    @ResponseBody
    public R delInfo(String id) {

        Log.info("删除申请记录, ID:{}", id);

        ApplyLogs applyLogs = applyLogsService.getOne(id);

        applyLogsService.delete(applyLogs);

        return R.success();
    }
}