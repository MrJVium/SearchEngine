package com.demo.mapreduce;

import com.demo.bayes.NBClassifier;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.*;
import org.wltea.analyzer.core.IKSegmenter;
import org.wltea.analyzer.core.Lexeme;

import java.io.IOException;
import java.io.StringReader;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AprilClassifyCount {
    public static NBClassifier nb = new NBClassifier();
    private static Pattern pattern = Pattern.compile("[^\u4E00-\u9FA5]");

    // 检查是否有除中文以外的特殊字符
    private static boolean check(String s){
        Matcher matcher = pattern.matcher(s);
        while (matcher.find()){
            return false;
        }

        return true;
    }


    public static class PredictMapper
            extends Mapper<Object, Text, Text, IntWritable> {

        private final static IntWritable one = new IntWritable(1);
        private Text word = new Text();

        public void map(Object key, Text value, Context context
        ) throws IOException, InterruptedException {
            String[] content = value.toString().split("\t");
            // 0:date  1:likecount  2:text
            StringReader sr=new StringReader(content[2]);
            IKSegmenter ik=new IKSegmenter(sr, true);
            Lexeme lex=null;
            String rs = "";
            while((lex=ik.next())!=null){
                if(check((lex.getLexemeText()))) {
                    word.set("1_" + lex.getLexemeText());
                    context.write(word, one);
                    word.set("4_"+lex.getLexemeText()+'_'+content[0]);
                    context.write(word, one);
                }
                rs += lex.getLexemeText()+" ";
            }
            String type = nb.predict(rs);
            word.set("2_"+type+"_"+content[0]);
            context.write(word, one);
            word.set("3_"+type);
            context.write(word, one);
        }

    }

    public static class IntSumReducer
            extends Reducer<Text, IntWritable, Text, IntWritable> {
        private IntWritable result = new IntWritable();
        private Text word = new Text();
        private MultipleOutputs<Text, IntWritable> mos;

        @Override
        protected void setup(Reducer<Text, IntWritable, Text, IntWritable>.Context context)
                throws IOException, InterruptedException {

            mos = new MultipleOutputs<>(context);
        }

        public void reduce(Text key, Iterable<IntWritable> values,
                           Context context
        ) throws IOException, InterruptedException {
            String keyStr = key.toString();
            String type = keyStr.substring(0,1);
            String[] contents = keyStr.split("_");
            word.set(contents[1]);
            int sum = 0;
            for (IntWritable val : values) {
                sum += val.get();
            }
            result.set(sum);

            if(type.equals("1")){
                mos.write(word, result,"wordCount");
            }
            else if(type.equals("2")){
                mos.write(word, result, "predict/"+contents[2]+"_predict");
            }
            else if(type.equals("3")){
                mos.write(word, result, "typeCount");
            }else if(type.equals("4")){
                mos.write(word, result, "wordCount/"+contents[2]+"_wordCount");
            }
        }

        @Override
        protected void cleanup(Reducer<Text, IntWritable, Text, IntWritable>.Context context)
                throws IOException, InterruptedException {
            mos.close();
        }
    }

    public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "sentiment analyze");
        job.setJarByClass(AprilClassifyCount.class);
        job.setMapperClass(AprilClassifyCount.PredictMapper.class);
        job.setCombinerClass(AprilClassifyCount.IntSumReducer.class);
        job.setReducerClass(AprilClassifyCount.IntSumReducer.class);

//        MultipleOutputs.addNamedOutput(job,"wordCount", TextOutputFormat.class,Text.class,IntWritable.class);
//        MultipleOutputs.addNamedOutput(job,"predict", TextOutputFormat.class,Text.class,IntWritable.class);
//        MultipleOutputs.addNamedOutput(job,"typeCount", TextOutputFormat.class,Text.class,IntWritable.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        LazyOutputFormat.setOutputFormatClass(job, TextOutputFormat.class);
//        FileInputFormat.addInputPath(job, new Path(args[0]));
//        FileOutputFormat.setOutputPath(job, new Path(args[1]));

//        //输入文件的路径
//        FileInputFormat.addInputPaths(job, "source/word");
//
//        //输出文件的路径
//        FileOutputFormat.setOutputPath(job, new Path("source/output"));
        FileInputFormat.setInputPaths(job, new Path("file:/Users/vium/IdeaProjects/sentiment-analyze/hadoopdemo/source/word/April"));
        FileOutputFormat.setOutputPath(job, new Path("file:/Users/vium/IdeaProjects/sentiment-analyze/hadoopdemo/source/output/April"));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }


}
