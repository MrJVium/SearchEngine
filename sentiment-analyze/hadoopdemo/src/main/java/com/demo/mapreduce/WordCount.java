package com.demo.mapreduce;

import java.io.*;
import java.util.StringTokenizer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Partitioner;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class WordCount {
    private static Pattern pattern = Pattern.compile("[^\u4E00-\u9FA5]");


    public static class TokenizerMapper
            extends Mapper<Object, Text, Text, IntWritable> {

        private final static IntWritable one = new IntWritable(1);
        private Text word = new Text();

        public void map(Object key, Text value, Context context
        ) throws IOException, InterruptedException {

            StringTokenizer itr = new StringTokenizer(value.toString());
            while (itr.hasMoreTokens()) {
                word.set(itr.nextToken());
                context.write(word, one);
            }
        }

    }

    public static class Partition extends Partitioner<Text, IntWritable> {
        @Override
        public int getPartition(Text key, IntWritable value,
                                int numPartitions) {
            String s = key.toString();
            int k = s.toLowerCase().charAt(0) - 'a';
            if (k>=0 || k < 26)
                return k;
            else
                return 25;
        }

    }

    public static class IntSumReducer
            extends Reducer<Text, IntWritable, Text, IntWritable> {
        private IntWritable result = new IntWritable();

        public void reduce(Text key, Iterable<IntWritable> values,
                           Context context
        ) throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable val : values) {
                sum += val.get();
            }

            result.set(sum);
            context.write(key, result);
        }
    }


    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "word count");
        job.setJarByClass(WordCount.class);
        job.setMapperClass(TokenizerMapper.class);
        job.setCombinerClass(IntSumReducer.class);
        job.setReducerClass(IntSumReducer.class);
        job.setPartitionerClass(Partition.class);
        job.setNumReduceTasks(26);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);


//        FileInputFormat.addInputPath(job, new Path(args[0]));
//        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        //输入文件的路径
//        FileInputFormat.setInputPaths(job, new Path("/user/vium/source/wordcount/word"));
//        FileOutputFormat.setOutputPath(job, new Path("/user/vium/source/wordcount/output"));
//        //输出文件的路径
//        FileOutputFormat.setOutputPath(job, new Path("source/output"));
        FileInputFormat.setInputPaths(job, new Path("file:/Users/vium/IdeaProjects/sentiment-analyze/hadoopdemo/source/wordcount/word"));
        FileOutputFormat.setOutputPath(job, new Path("file:/Users/vium/IdeaProjects/sentiment-analyze/hadoopdemo/source/wordcount/output"));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}