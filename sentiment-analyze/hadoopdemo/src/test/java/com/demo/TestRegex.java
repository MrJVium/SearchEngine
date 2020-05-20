package com.demo;

import org.junit.Test;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class TestRegex {

    private static Pattern pattern = Pattern.compile("[^\u4E00-\u9FA5]");
    private static Matcher matcher;

    private static boolean check(String s){
        matcher = pattern.matcher(s);
        while (matcher.find()){
            return false;
        }

        return true;
    }


    @Test
    public void testWeiboAt(){
        String comment = "//@金惠国丶://@微不足道7606://@alan8616:石正丽伙同美国人，从事的“功能获得性”研究，实际上就是人工重组，转基因病毒。//@alan8616:在转基因问题上，国家和社会，冤枉了很多反对转基因的好人。科学研究自然规律，转基因违背自然规律。//@alan8616:科学出错，会导致法律出错，会冤枉很多人。因为判\n";
        String s = comment.replaceAll("//@.*?:","");
        System.out.println(s);
    }

    @Test
    public void testMonth(){
        String time = "2020-02-01";

        System.out.println(time.split("-")[1].equals("02"));
    }
}
