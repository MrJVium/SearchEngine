package com.demo.mapreduce;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;

public class TestHadoop {


    public  class MyMapper extends Mapper<LongWritable, Text, Text, LongWritable> {

        @Override
        protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {

            //value 为读入文件的行，每一行都会调用map方法
            String[] split = value.toString().split(",");
            if (split.length < 0) {
                return;
            }
            String words = split[0];
            long num = Long.parseLong(split[1]);
            //以key-value的形式输出，随后reduce根据key进行聚合计算
            //如：(shanghai 5),(shanghai 2),(beijing,3),(shanghai 1),(beijing,6)
            context.write(new Text(words), new LongWritable(num));
            System.out.println(words);
        }
    }

    public class MyReduce extends Reducer<Text, LongWritable, Text, LongWritable> {
        @Override
        protected void reduce(Text key, Iterable<LongWritable> values, Context context) throws IOException, InterruptedException {
            //同一个key的键值对被聚合为一个可迭代的对象values
            //此时key=shanghai,values=5,2,1
            //每个key都调用一次reduce方法
            long count = 0L;
            for (LongWritable value : values) {
                count += value.get();
            }
            context.write(key, new LongWritable(count));
        }

    }


    public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {
        Configuration conf = new Configuration();
//        conf.set("mapred.job.tracker", "local");
        conf.set("fs.default.name", "local");
        Job job = null;
        try {
            job = Job.getInstance(conf);
        } catch (IOException e) {
            e.printStackTrace();

        }
        //设置jar包的类，为本类
        job.setJarByClass(TestHadoop.class);

        //设置Mapper和Reducer的类，要不怎么知道用哪个mapper和Reducer呢
        job.setMapperClass(MyMapper.class);
        job.setReducerClass(MyReduce.class);

        //设置Mapper的输出键、值类型
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(LongWritable.class);

        //设置Reducer的输出键、值类型
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(LongWritable.class);

        //如果文件在hdfs上地址需要如下这样设置
//        FileInputFormat.setInputPaths(job, "hdfs://127.0.0.1:8088/source/word/");
//        FileOutputFormat.setOutputPath(job, new Path("hdfs://127.0.0.1:8088/output/word"));

        //输入文件的路径
        FileInputFormat.setInputPaths(job, "source/word");

        //输出文件的路径
        FileOutputFormat.setOutputPath(job, new Path("source/output"));

        //提交任务
        job.waitForCompletion(true);
    }


}
