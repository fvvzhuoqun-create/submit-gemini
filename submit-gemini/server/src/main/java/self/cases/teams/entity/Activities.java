package self.cases.teams.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.io.Serializable;

/**
 * 数据实体类
 * 活动信息
 */
@TableName(value = "activities")
public class Activities implements Serializable {

	private static final long serialVersionUID = 1L;

	@TableId(value = "id")
	private String id;

	@TableField(value = "name")
	private String name;

	@TableField(value = "comm")
	private String comm;

	@TableField(value = "detail")
	private String detail;

	@TableField(value = "ask")
	private String ask;

	@TableField(value = "total")
	private Integer total;

	@TableField(value = "active_time")
	private String activeTime;

	@TableField(value = "team_id")
	private String teamId;

	// --- 新增媒体文件字段 ---
	@TableField(value = "media_file")
	private String mediaFile;

	public String getMediaFile() {
		return mediaFile;
	}

	public void setMediaFile(String mediaFile) {
		this.mediaFile = mediaFile;
	}
	// ---------------------

	public String getId(){ return id; }
	public void setId(String id){ this.id = id; }
	public String getName(){ return name; }
	public void setName(String name){ this.name = name; }
	public String getComm(){ return comm; }
	public void setComm(String comm){ this.comm = comm; }
	public String getDetail(){ return detail; }
	public void setDetail(String detail){ this.detail = detail; }
	public String getAsk(){ return ask; }
	public void setAsk(String ask){ this.ask = ask; }
	public Integer getTotal(){ return total; }
	public void setTotal(Integer total){ this.total = total; }
	public String getActiveTime(){ return activeTime; }
	public void setActiveTime(String activeTime){ this.activeTime = activeTime; }
	public String getTeamId(){ return teamId; }
	public void setTeamId(String teamId){ this.teamId = teamId; }

	@Override
	public String toString() {
		return "Activities [id=" + id + ", name=" + name + ", comm=" + comm + ", detail=" + detail + ", ask=" + ask + ", total=" + total + ", activeTime=" + activeTime + ", teamId=" + teamId + ", mediaFile=" + mediaFile + "]";
	}
}