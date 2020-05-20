package com.demo;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.junit.Test;

import java.net.URI;

public class TestHadoop {

    @Test
    public void testHadoop(){
        try{
            String url = "hdfs://localhost:9000";
            String filepath =  "/input/file1.txt";

            Configuration conf = new Configuration();
            FileSystem fs = FileSystem.get(URI.create(url),conf);

            if (fs.exists(new Path(filepath))){
                System.out.println(filepath+"文件存在");
            }else{
                System.out.println(filepath+"文件不存在");
            }

        }catch (Exception e){
            e.printStackTrace();
        }
    }
    @Test
    public void tt(){
        String s = "asds";

        int a = 'a'-'a';
        System.out.println(s.charAt(0));
    }
}
