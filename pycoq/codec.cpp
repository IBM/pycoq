// sample usage:  g++ -O3 codec.cpp -o test && time ./test ../tests/sexp.txt

// sample input
// (a b c)
// (c b a)
// ()
// (()  ()  )
// (abb(()d)bcc)
// (abb"b\"c\\c"())
//
// ( ( e f g ) a ( e f g ) ( b c ) d)

// sample output
// 1 2 3 -3  : size 4
// 3 2 1 -3  : size 4
// 0  : size 1
// 0 0 -2  : size 3
// 4 0 5 -2 6 -3  : size 6
// 4 7 0 -3  : size 4
//  : size 0
// 8 9 10 -3 1 8 9 10 -3 2 3 -2 5 -5  : size 14
// done: 36


#include <sstream> 
#include <string> 
#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_map> 

using namespace std;

int const ERR_UNFINISHED_ESCAPE =  -1;
int const ERR_UNFINISHED_QUOTE  = -2;
int const TOKEN_WORD  = 0;
int const TOKEN_OPEN_PAR  = 1;
int const TOKEN_CLOSE_PAR  = 2;
int const TOKEN_EOF = -2;
int const TOKEN_ERR = -3;

struct Token {
  int code;
  string value;
};


struct NodeI {
  int value;
  vector<NodeI*> items;
};


class TokenGenerator {
  string s;
  int n;
  int pos;

public:
  TokenGenerator(string &s, int pos) {
    this->s = s;
    this->pos = pos;
    this->n = s.size();
  }

  int seek_end_word() {
    int pos = this->pos;
    if (s[pos] == '"') {
      pos++;
      while (pos < n && s[pos] != '"') {
	if (s[pos] == '\\') {
	  pos++;
	  if (pos == n) return ERR_UNFINISHED_ESCAPE;
	}
	pos++;
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

  Token next_token() {
    Token t;
    while (pos < n && s[pos] == ' ') pos++;
    if (pos == n) {
      t.code = TOKEN_EOF;
      return t;
    }
    if (s[pos] == '(') {
      pos++;
      t.code =  TOKEN_OPEN_PAR;
      return t;
    }
    if (s[pos] == ')') {
      pos++;
      t.code = TOKEN_CLOSE_PAR;
      return t;
    }


    int next_pos = seek_end_word();


    if (next_pos > pos) {
      int old_pos = pos;
      pos = next_pos;
      t.code = TOKEN_WORD;
      t.value = s.substr(old_pos, pos - old_pos);
      return t;
    }
    t.code = TOKEN_EOF;
    return t;
  }
};



class Codec {
  NodeI* root;
  unordered_map<string, int> *enc;
  unordered_map<int, string> *dec;


  NodeI* build_tree(TokenGenerator &tg) {
    Token t = tg.next_token();
    if (t.code == TOKEN_WORD) {
      if (enc->find(t.value) == enc->end()) {
	(*enc)[t.value] = enc->size() + 1;
	(*dec)[enc->size()]=t.value;
      }
      int value = (*enc)[t.value];
      NodeI* node = new NodeI();
      node->value = value;
      return node;
    } else {
      if (t.code == TOKEN_OPEN_PAR) {
	vector<NodeI*> items;
	NodeI* next;
	while ((next = build_tree(tg)) != NULL) items.push_back(next);
	NodeI* node = new NodeI;
	node->items = items;
	node->value = 0;
	return node;
      } else
	return NULL;
    }
  }

  void postfix_(NodeI* root, vector<int> &stack) {
    if (root->value != 0) stack.push_back(root->value);
    else {
      for(auto&& node: root->items) {
	postfix_(node, stack);
      }
      stack.push_back(-root->items.size());
    }
  }


public:

  int encode(string &word) {
    return (*enc)[word];
  }

  string decode(int x) {
    return (*dec)[x];
  }
  
  vector<int> postfix() {
    vector<int> stack;
    if (root == NULL) return stack;
    postfix_(root, stack);
    return stack;
  }
  
  Codec(TokenGenerator &tg, unordered_map<string, int>  &enc, unordered_map<int,string> &dec) {
    this->enc = &enc;
    this->dec = &dec;
    this->root = build_tree(tg);
  }

  
};

void print(vector<int> &v) {
   for (int x: v) cout << x << " ";
   cout << " : size " << v.size() << "\n";
}


int main(int argc, char* argv[]) {
  if (argc != 2) {
    cout << "usage: test <input.txt>\n";
    return -1;
  }

  string line;
  ifstream fin;
  fin.open(argv[1]);
  int cnt = 0;
  
  unordered_map<string, int> enc_global;
  unordered_map<int, string> dec_global;
  while (getline(fin, line)) {
    TokenGenerator tg(line, 0);
    Codec c(tg, enc_global, dec_global);
    vector<int> stack =  c.postfix();
    print(stack);
    cnt += stack.size();
  }
  cout << "done: " << cnt <<  "\n";
  fin.close();
}
