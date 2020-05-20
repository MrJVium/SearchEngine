package com.demo;

import org.junit.Test;
import org.wltea.analyzer.core.IKSegmenter;
import org.wltea.analyzer.core.Lexeme;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;

public class TestIK {
    @Test
    public void Ik() throws IOException {
        String text="我担心，哪天去了个现任总统，估计世界战争快开始了。";
        StringReader sr=new StringReader(text);
        IKSegmenter ik=new IKSegmenter(sr, true);
        Lexeme lex=null;
        String rs = "";
        while((lex=ik.next())!=null){
            rs += lex.getLexemeText()+" ";
        }
        System.out.println(rs);
    }

    @Test
    public void aa(){
        System.out.println("a\ta");
    }

    @Test
    public void f(){
        System.out.println(File.separator);
    }
}
