package self.cases.teams.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import self.cases.teams.dao.MembersDao;
import self.cases.teams.dao.TeamsDao;
import self.cases.teams.entity.Members;
import self.cases.teams.entity.Teams;
import self.cases.teams.msg.PageData;
import self.cases.teams.entity.ApplyLogs;
import self.cases.teams.dao.ApplyLogsDao;
import self.cases.teams.service.ApplyLogsService;
import self.cases.teams.utils.DateUtils;
import self.cases.teams.utils.IDUtils;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service("applyLogsService")
public class ApplyLogsServiceImpl implements ApplyLogsService {

    @Autowired
    private MembersDao membersDao;

    @Autowired
    private ApplyLogsDao applyLogsDao;

    @Autowired
    private TeamsDao teamsDao;

    @Override
    @Transactional
    public void add(ApplyLogs applyLogs) {

        applyLogsDao.insert(applyLogs);
    }

    @Override
    @Transactional
    public void update(ApplyLogs applyLogs) {

        if(applyLogs.getStatus() != null && applyLogs.getStatus() == 1){

            Members member = new Members();
            member.setId(IDUtils.makeIDByCurrent());
            member.setCreateTime(DateUtils.getNowDate());
            member.setUserId(applyLogs.getUserId());
            member.setTeamId(applyLogs.getTeamId());

            membersDao.insert(member);

            Teams teams = teamsDao.selectById(applyLogs.getTeamId());
            teams.setTotal(teams.getTotal() + 1);
            teamsDao.updateById(teams);
        }

        applyLogsDao.updateById(applyLogs);
    }

    @Override
    @Transactional
    public void delete(ApplyLogs applyLogs) {

        applyLogsDao.deleteById(applyLogs);
    }

    @Override
    @Transactional(readOnly = true, propagation = Propagation.SUPPORTS)
    public String checkApply(String userId, String teamId){

        // 1. 检查是否已经是该社团成员
        QueryWrapper<Members> qwMem = new QueryWrapper<>();
        qwMem.eq("user_id", userId);
        qwMem.eq("team_id", teamId);
        if(membersDao.selectCount(qwMem) > 0){
            return "您已经是该社团成员，无需重复申请";
        }

        // 2. 检查是否有待审核的申请 (status=0)
        QueryWrapper<ApplyLogs> qwPending = new QueryWrapper<>();
        qwPending.eq("user_id", userId);
        qwPending.eq("team_id", teamId);
        qwPending.eq("status", 0);
        if(applyLogsDao.selectCount(qwPending) > 0){
            return "申请审核中，请耐心等待";
        }

        // 3. 检查冷静期 (status=2 为拒绝)
        QueryWrapper<ApplyLogs> qwReject = new QueryWrapper<>();
        qwReject.eq("user_id", userId);
        qwReject.eq("team_id", teamId);
        qwReject.eq("status", 2);
        qwReject.orderByDesc("create_time"); // 获取最近一次被拒绝的记录

        List<ApplyLogs> rejects = applyLogsDao.selectList(qwReject);
        if(rejects != null && !rejects.isEmpty()){
            ApplyLogs lastReject = rejects.get(0);
            try {
                // 计算距离上次被拒过去了多少天
                Date rejectDate = DateUtils.parseDate(lastReject.getCreateTime(), DateUtils.DATETIME_DEFAULT_FORMAT);
                Date now = new Date();
                long diffInfo = now.getTime() - rejectDate.getTime();
                long days = diffInfo / (1000 * 60 * 60 * 24);

                // 获取社团设定的冷静期
                Teams team = teamsDao.selectById(teamId);
                int cd = team.getCooldown(); // 如果实体类里处理了null，这里直接调用即可；否则建议再次判空

                if(days < cd){
                    return "申请曾被拒绝，请在 " + (cd - days) + " 天后再次申请";
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        return null; // 返回 null 表示校验通过
    }

    @Override
    @Transactional(readOnly = true, propagation = Propagation.SUPPORTS)
    public ApplyLogs getOne(String id) {

        ApplyLogs applyLogs = applyLogsDao.selectById(id);

        return applyLogs;
    }

    @Override
    @Transactional(readOnly = true, propagation = Propagation.SUPPORTS)
    public PageData getManPageInfo(Long pageIndex, Long pageSize, String userId, String teamName, String userName) {

        Page<Map<String, Object>> page =
                applyLogsDao.qryManPageInfo(new Page<Map<String, Object>>(pageIndex, pageSize), userId, teamName, userName);

        return parsePage(page);
    }

    @Override
    @Transactional(readOnly = true, propagation = Propagation.SUPPORTS)
    public PageData getPageInfo(Long pageIndex, Long pageSize, String userId, String teamName, String userName) {

        Page<Map<String, Object>> page =
                applyLogsDao.qryPageInfo(new Page<Map<String, Object>>(pageIndex, pageSize), userId, teamName, userName);

        return parsePage(page);
    }

    /**
     * 转化分页查询的结果
     */
    public PageData parsePage(Page<Map<String, Object>> p) {

        PageData pageData = new PageData(p.getCurrent(), p.getSize(), p.getTotal(), p.getRecords());

        return pageData;
    }
}