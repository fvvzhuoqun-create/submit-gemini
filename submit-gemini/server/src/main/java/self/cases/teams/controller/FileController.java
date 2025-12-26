package self.cases.teams.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import self.cases.teams.msg.R;

import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.util.UUID;

@RestController
@RequestMapping("/files")
public class FileController {

    // 图片存储的基础路径，建议放在项目根目录下的 upload 文件夹
    private static final String BASE_PATH = System.getProperty("user.dir") + "/upload/";

    /**
     * 文件上传
     */
    @PostMapping("/upload")
    public R upload(MultipartFile file) throws IOException {
        if (file.isEmpty()) {
            return R.error("上传失败，请选择文件");
        }

        File dir = new File(BASE_PATH);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        String originalFilename = file.getOriginalFilename();
        String suffix = "";
        // 防止文件名为空导致的异常
        if (originalFilename != null && originalFilename.contains(".")) {
            suffix = originalFilename.substring(originalFilename.lastIndexOf("."));
        }

        String fileName = UUID.randomUUID().toString() + suffix;

        File dest = new File(BASE_PATH + fileName);
        file.transferTo(dest);

        // 返回文件名，前端通过 /files/{fileName} 访问
        return R.success("上传成功", fileName);
    }

    /**
     * 图片回显/下载
     * 【已注释】
     * 原因：已在 Application.java 中配置 addResourceHandlers 接管静态资源访问。
     * 这里的代码会强制所有文件为 image/jpeg 且不支持 Range 请求（导致视频无法拖动），
     * 所以必须注释掉，避免冲突。
     */
//    @GetMapping("/{fileName}")
//    public void download(@PathVariable String fileName, HttpServletResponse response) throws IOException {
//        File file = new File(BASE_PATH + fileName);
//        if (!file.exists()) {
//            return;
//        }
//
//        FileInputStream fis = new FileInputStream(file);
//        response.setContentType("image/jpeg"); // 这里简单处理，实际可根据后缀判断
//
//        OutputStream os = response.getOutputStream();
//        byte[] buffer = new byte[1024];
//        int len;
//        while ((len = fis.read(buffer)) != -1) {
//            os.write(buffer, 0, len);
//        }
//        fis.close();
//    }
}