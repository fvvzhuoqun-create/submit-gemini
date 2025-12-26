package self.cases.teams;

import com.alibaba.fastjson.serializer.SerializerFeature;
import com.alibaba.fastjson.support.config.FastJsonConfig;
import com.alibaba.fastjson.support.spring.FastJsonHttpMessageConverter;
import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.http.HttpMessageConverters;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.http.MediaType;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry; // 【新增引入】
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.ArrayList;
import java.util.List;

@SpringBootApplication
@MapperScan({"self.cases.teams.dao"})
@EnableCaching
public class Application implements WebMvcConfigurer {

    /**
     * JSON格式转换器
     */
    @Bean
    public HttpMessageConverters fastJsonHttpMessageConverters() {
        FastJsonHttpMessageConverter fastConverter = new FastJsonHttpMessageConverter();
        FastJsonConfig fastJsonConfig = new FastJsonConfig();
        fastJsonConfig.setSerializerFeatures(SerializerFeature.PrettyFormat);
        List<MediaType> fastMedisTypes = new ArrayList<>();
        fastMedisTypes.add(MediaType.APPLICATION_JSON);
        fastConverter.setSupportedMediaTypes(fastMedisTypes);
        fastConverter.setFastJsonConfig(fastJsonConfig);
        HttpMessageConverter<?> converter = fastConverter;
        return new HttpMessageConverters(converter);
    }

    /**
     * 添加MySQL分页查询
     */
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }

    /**
     * 【新增关键配置】配置静态资源映射
     * 作用：告诉 Spring Boot 当收到 /files/** 的请求时，去本地硬盘的 upload 目录找文件
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 获取当前工作目录下的 upload 文件夹路径
        // 注意：在 Linux 服务器上，请确保 jar 包同级目录下有 upload 文件夹，且有读写权限
        String path = System.getProperty("user.dir") + "/upload/";

        // 映射 URL /files/** 到本地文件系统的 upload 目录
        // "file:" 前缀是必须的，表示文件系统路径
        registry.addResourceHandler("/files/**")
                .addResourceLocations("file:" + path);
    }

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                        .allowedOrigins("*")
                        .allowCredentials(true)
                        .allowedMethods("GET", "POST", "DELETE", "PUT","PATCH")
                        .maxAge(3600);

            }
        };
    }

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}