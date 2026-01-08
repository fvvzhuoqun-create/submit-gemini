package util;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;

public class QTTable {
    public ArrayList<QTInfo> QTList = new ArrayList<>();

    // ?? innerIdSeqen ????????ID?????? clear ???
    // public static boolean flag = true; // ?????????????????

    public void addQTInfo(QTInfo info) {
        QTList.add(info);
    }

    public void addQTInfo(int index, QTInfo info) {
        QTList.add(index, info);
    }

    public QTInfo get(int index) {
        if (index >= 0 && index < QTList.size()) {
            return QTList.get(index);
        }
        return null; // ??????
    }

    public QTInfo remove(int index) {
        // ??????????? 0-based ???
        // ???????? 1-based ID???? index - 1
        if (index >= 0 && index < QTList.size()) {
            return QTList.remove(index);
        }
        return null;
    }

    public void clear() {
        QTList.clear();
        QTInfo.innerIdSeqen = QTInfo.START; // ?? QTInfo ????????
    }

    public void printQTTable() {
        File dir = new File("test");
        if (!dir.exists()) {
            dir.mkdirs(); // ????
        }
        File f = new File(dir, "resultYuYi.txt");

        // ?? try-with-resources ?????
        try (BufferedWriter output = new BufferedWriter(new FileWriter(f))) {
            for (QTInfo tmp : QTList) {
                output.write(tmp.toString());
                output.newLine(); // ????????? toString ?????
            }
            System.out.println("?????????: " + f.getAbsolutePath());
        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("??????");
        }
    }

    public int size() {
        return QTList.size();
    }
}