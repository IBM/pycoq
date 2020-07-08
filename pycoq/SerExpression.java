// using Guava library BiMap https://guava.dev/releases/19.0/api/docs/com/google/common/collect/BiMap.html
// gownload guava-29.0-jre.jar from https://mvnrepository.com/artifact/com.google.guava/guava to the cur dir
// javac -classpath .:guava-29.0-jre.jar Sexp.java && time java -classpath .:guava-29.0-jre.jar Sexp ../tests/100Mb.txt > 100Mb.postfix.txt
// real	0m5.306s
// user	0m7.816s
// sys	0m0.484s


import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.stream.Stream;
import java.util.Arrays;
import java.util.ArrayList;
import com.google.common.collect.HashBiMap;
import com.google.common.collect.Lists;

public class Sexp {
    static int TOKEN_WORD = 0;
    static int TOKEN_OPEN_PAR = 1;
    static int TOKEN_CLOSE_PAR = 2;
    static int ERR_UNFINISHED_ESCAPE = -1;
    static int ERR_UNFINISHED_QUOTE = -2;

    static class NodeI {
	// exactly one field must be not null
	Integer value;
	ArrayList<NodeI> items;
    }


    static class Codec {
	private HashBiMap<String,Integer> bm;
	private NodeI root;
	Codec(TokenGenerator tg, HashBiMap<String,Integer> bm) {
	    this.bm = bm;
	    this.root = buildIndexTree(tg);
	}
	Codec(TokenGenerator tg) {
	    this.bm = HashBiMap.create();
	    this.root = buildIndexTree(tg);
	}



	private NodeI buildIndexTree(TokenGenerator tg) {
	    Token t = tg.nextToken();
	    if (t == null) return null;
	    if (t.code == TOKEN_WORD) {
		if (!bm.containsKey(t.value)) bm.put(t.value, bm.size() + 1);
		int value = bm.get(t.value);
		NodeI node = new NodeI();
		node.value = value;
		return node;
	    } else {
		if (t.code == TOKEN_OPEN_PAR) {
		    ArrayList<NodeI> items = new ArrayList<NodeI>();
		    NodeI next;
		    while ((next = buildIndexTree(tg)) != null) items.add(next);
		    NodeI node = new NodeI();
		    node.items = items;
		    return node;
		} else
		    return null;
	    }
	}


	public NodeI toIndexTree () {
	    return root;
	}

	private ArrayList<Integer> toPostFix_ (NodeI root, ArrayList<Integer> stack) {    if (root == null) return stack;
	    if (root.value != null) stack.add(root.value);
	    else {
		stack.add(-root.items.size());
		for (NodeI node: Lists.reverse(root.items)) {
		    stack = toPostFix_(node, stack);
		}
	    }
	    return stack;
	}

	public ArrayList<Integer> toPostFix() {
	    ArrayList<Integer> stack = new ArrayList<Integer>();
	    stack = toPostFix_(this.root, stack);
	    return stack;
	}

	private static String toString_ (NodeI root) {
	    if (root.value != null) return root.value.toString();
	    else {
		StringBuilder res = new StringBuilder();
		res.append('[');
		int cnt = 0;
		for (NodeI node: root.items) {
		    res.append(toString_(node));
		    if (cnt < root.items.size()-1) res.append(", ");
		    cnt++;
		}
		res.append(']');
		return res.toString();
	    }
	}

	public String toString() {
	    return toString_(this.root);
	}


	public HashBiMap<String,Integer> getIndex() {
	    return this.bm;
	}

	
    }

    static int depth(NodeI root) {
	if (root.items == null) return 1;
	else { 
	    int d = 0;
	    for (NodeI node: root.items)
		d = Math.max(d, depth(node));
	    return d + 1;
	}
    }




    static class Token {
	int code;
	String value;
	public Token(int code, String value) {
	    this.code = code;
	    this.value = value;
	}
	public String toString() {
	    return "(" + this.code + ", " + this.value + ")";
	}
    }


    static class TokenGenerator {
	char[] s;
	int n;
	int pos;
	public TokenGenerator(String s, int pos) {
	    // initialise generator with string and position
	    this.s = s.toCharArray();
	    this.n = s.length();
	    this.pos = pos;
	}

	public int seekEndWord() {
	    int pos = this.pos;
	    if (s[pos] == '"') {
		pos++;
		while (pos < n && s[pos] != '"') {
		    if (s[pos] == '\\') {
			if (pos + 1 >= n) return ERR_UNFINISHED_ESCAPE;
			else pos += 2;
		    } else pos++;
		}
		if (pos < n && s[pos] == '"') return pos + 1;
		else return ERR_UNFINISHED_QUOTE; 
	    } else {
		while (pos < n && !(s[pos] == '"' ||
				     s[pos] == '(' ||
				     s[pos] == ')' ||
				    s[pos] == ' ')) pos++;
		return pos;
	    }
	}
	    
	public Token nextToken() {
	    while (pos < n && s[pos] == ' ') pos++;
	    if (pos == n) return null;
	    if (s[pos] == '(') {
		pos++;
		return (new Token(TOKEN_OPEN_PAR,"("));
	    }
	    if (s[pos] == ')') {
		pos++;
		return (new Token(TOKEN_CLOSE_PAR,")"));
	    }
	    int next_pos = seekEndWord();
	    if (next_pos > pos) {
		int old_pos = pos;
		pos = next_pos;
		return (new Token(TOKEN_WORD, new String(s, old_pos, pos - old_pos)));
	    }
	    return null;
	}

	public ArrayList<Token> asList() {
	    // returns remaining tokens as list in ArrayList data structure 
	    Token t;
	    ArrayList<Token> ts = new ArrayList<Token>();
	    while ((t = nextToken()) != null) ts.add(t);
	    return ts;
	}
	
    }

    public static void printUsage() {
	System.out.println("usage: java Sexp filename.txt\n" + 
			   "Each line in the input filename.txt is sexpression. " + 
			   "If argument is empty, assume standard input.");
    }

    public static void print(String msg) {
	System.out.println(msg);
    }


    public static void main(String[] args)
	throws IOException    {
	BufferedReader fin;
	if (args.length == 0) {
	    fin = new BufferedReader (new InputStreamReader(System.in));
	} else if (args.length == 1) {
	    fin = new BufferedReader (new FileReader(args[0]));
	} else {
	    printUsage();
	    return;
	}
	String[] lines = fin.lines().toArray(String[]::new);

	int cnt = 0;
	for (String line: lines) {
	    //TokenGenerator tg = new TokenGenerator(line, 0);
	    //print("" + tg.asList().size());
	    Codec c = new Codec(new TokenGenerator(line,0));
	    //print(c.toString());
	    int postfix_size = c.toPostFix().size(); 
	    print("" + postfix_size);
	    //print(c.toPostFix().toString());
	    //cnt += postfix_size;
	}
	print(""+cnt);
    }
}
