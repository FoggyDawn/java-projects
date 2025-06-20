package com.puppycrawl.tools.checkstyle;

/**
 * Describe class InputMagicNumber
 * @author Rick Giles
 * @version 6-May-2003
 */
public class InputMagicNumber {
    public void magicMethod() {
        //constants, ignore
        final int INT_CONST = 101;
        final long LONG_CONST1 = 100L;
        final long LONG_CONST2 = 100l;
        final float FLOAT_CONST1 = 1.5F;
        final float FLOAT_CONST2 = 1.5f;
        final double DOUBLE_CONST1 = 1.5D;
        final double DOUBLE_CONST2 = 1.5d;
        final double DOUBLE_CONST3 = 1.5;

        //ignore by default
        int int_var1 = 1;
        int int_var2 = (2);
        long long_var1 = 0L;
        long long_var2 = 0l;
        double double_var1 = 0D;
        double double_var2 = 0d;

        int[] int_array = new int[2];

        int_var1 = 1 + 2;
        int_var1 += 1;
        double_var1 = 1.0 + 2.0;

        for (int i = 0; i < 2; i++);

        if (1 < 2);
        
        if (1.0 < 2.0);

        //magic numbers
        int int_magic1 = 3;
        double double_magic1 = 1.5;
        int int_magic2 = (3 + 4);
        
        int_array = new int[3];
        
        int_magic1 += 3;
        double_magic1 *= 1.5;
        
        for (int j = 3; j < 5; j += 3) {
            int_magic1++;
        }

        if (int_magic1 < 3) {
            int_magic1 = int_magic1 + 3;
        }
        
        //octal
        int octalVar0 = 00;
        int octalVar8 = 010;
        int octalVar9 = 011;
        
        long longOctalVar8 = 010L;
        long longOctalVar9 = 011l;
        
        //hex
        int hexVar0 = 0x0;
        int hexVar16 = 0x10;
        int hexVar17 = 0X011;
        long longHexVar0 = 0x0L;
        long longHexVar16 = 0x10L;
        long longHexVar17 = 0X11l;       
    }
}

interface Blah
{
  int LOW = 5;
  int HIGH = 78;
}

class ArrayMagicTest
{
    private static final int[] NONMAGIC = {3};
    private int[] magic = {3};
    private static final int[][] NONMAGIC2 = {{1}, {2}, {3}};
}

/** test long hex */
class LongHex
{
    long l = 0xffffffffL;
}

/** test signed values */
class Signed
{
    public static final int CONST_PLUS_THREE = +3;
    public static final int CONST_MINUS_TWO = -2;
    private int mPlusThree = +3;
    private int mMinusTwo = -2;
    private double mPlusDecimal = +3.5;
    private double mMinusDecimal = -2.5; 
}

/** test octal and hex negative values */
class NegativeOctalHex
{
    private int hexIntMinusOne = 0xffffffff;
    private long hexLongMinusOne = 0xffffffffffffffffL;
    private long hexIntMinValue = 0x80000000;
    private long hexLongMinValue = 0x8000000000000000L;
    private int octalIntMinusOne = 037777777777;
    private long octalLongMinusOne = 01777777777777777777777L;
    private long octalIntMinValue = 020000000000;
    private long octalLongMinValue = 01000000000000000000000L;
}

class Cast
{
    public static final int TESTINTVAL = (byte) 0x80;
}

class ComplexAndFlagged
{
    public static final java.util.List MYLIST = new java.util.ArrayList()
    {
        public int size() 
        {
            // should be flagged although technically inside const definition
            return 378;
        }
    };
}

class ComplexButNotFlagged
{
    // according to user feedback this is typical code that should not be flagged
    // (at least in the default configuration of MagicNumberCheck)
    public static final Integer DEFAULT_INT = new Integer(27);
    public static final int SECS_PER_DAY = 24 * 60 * 60;
    public static final javax.swing.border.Border STD_BORDER = 
        javax.swing.BorderFactory.createEmptyBorder(3, 3, 3, 3);
}

enum MyEnum
{
    A(3),
    B(54);

    private MyEnum(int value)
    {
        
    }
}
