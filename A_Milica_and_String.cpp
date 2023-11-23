#include<bits/stdc++.h>
using namespace std;
#define pb push_back
#define mk make_pair
#define ll long long
#define f first
#define s second
int X[4]={0,0,1,-1};
int Y[4]={1,-1,0,0};
#define inf 9223372036854775807
int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
                 
    int t;
    cin>>t;
    while(t--){
        int n,k;
        string s;
        cin>>n>>k;
        cin>>s;
        int count=0;
        int index=0;
        for(int i=0;i<n;i++){
            if(s[i]=='B')
                count++;
        }
        if(count<k)
        {
            for(int i=0;i<n;i++){
                if(s[i]=='A')
                {
                    count++;
                }
                if(count==k)
                {
                    cout<<"1\n"<<i+1<<" B\n";
                                break;
                }
            }
        }
        else if(count==k)
        {   
            cout<<"0\n";
        }
        else{
            for(int i=0;i<n;i++){
                if(s[i]=='B')
                {
                    count--;
                }
                if(count==k)
                {
                    cout<<"1\n"<<i+1<<" A\n";
                                break;
                }
                
            }

        }
    }
    return 0;
}