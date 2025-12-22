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

import self.cases.teams.utils.DateUtils;
import self.cases.teams.utils.IDUtils;
import self.cases.teams.msg.R;
import self.cases.teams.msg.PageData;

import self.cases.teams.entity.Users;
import self.cases.teams.service.UsersService;

/**
 * 系统请求响应控制器
 * 系统用户
 */
@Controller
@RequestMapping("/users")
public class UsersController extends BaseController {

    protected static final Logger Log = LoggerFactory.getLogger(UsersController.class);

    @Autowired
    private UsersService usersService;

    // ... 原有 index, getInfo, getPageInfos 方法保持不变 ...

    @RequestMapping("")
    public String index() {
        return "pages/Users";
    }

    @GetMapping("/info")
    @ResponseBody
    public R getInfo(String id) {
        Log.info("查找指定系统用户，ID：{}", id);
        Users users = usersService.getOne(id);
        return R.successData(users);
    }

    @GetMapping("/page")
    @ResponseBody
    public R getPageInfos(Long pageIndex, Long pageSize,
                          Users users) {
        Log.info("分页查找系统用户，当前页码：{}，"
                        + "每页数据量：{}, 模糊查询，附加参数：{}", pageIndex,
                pageSize, users);
        PageData page = usersService.getPageInfo(pageIndex, pageSize, users);
        return R.successData(page);
    }

    @PostMapping("/add")
    @ResponseBody
    public R addInfo(Users users) {
        if(usersService.getUserByUserName(users.getUserName()) == null){
            users.setId(IDUtils.makeIDByCurrent());
            users.setCreateTime(DateUtils.getNowDate());
            Log.info("添加系统用户，传入参数：{}", users);
            usersService.add(users);
            return R.success();
        }else{
            return R.warn("用户账号已存在，请重新输入");
        }
    }

    @PostMapping("/upd")
    @ResponseBody
    public R updInfo(Users users) {
        Log.info("修改系统用户，传入参数：{}", users);
        usersService.update(users);
        return R.success();
    }

    @PostMapping("/del")
    @ResponseBody
    public R delInfo(String id) {
        if(usersService.isRemove(id)){
            Log.info("删除系统用户, ID:{}", id);
            Users users = usersService.getOne(id);
            usersService.delete(users);
            return R.success();
        }else{
            return R.warn("用户存在关联社团，无法移除");
        }
    }

    /**
     * 新增功能：找回密码/重置密码
     * 验证用户名和手机号是否匹配，如果匹配则更新密码
     */
    @PostMapping("/resetPwd")
    @ResponseBody
    public R resetPwd(Users users) {
        Log.info("用户尝试重置密码，账号：{}，手机号：{}", users.getUserName(), users.getPhone());

        // 1. 根据用户名查找用户
        Users existUser = usersService.getUserByUserName(users.getUserName());

        if (existUser == null) {
            return R.warn("用户账号不存在");
        }

        // 2. 校验手机号是否匹配
        if (existUser.getPhone() == null || !existUser.getPhone().equals(users.getPhone())) {
            return R.warn("预留手机号验证失败，无法重置密码");
        }

        // 3. 更新密码
        existUser.setPassWord(users.getPassWord());
        usersService.update(existUser);

        return R.success();
    }
}