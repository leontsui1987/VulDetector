#include<string.h>
#include<stdio.h>
#include<stdlib.h>

char var[256][64]={0},func[256][64]={0};
int var_c=0,func_c=0;

char *str_replace(char *in, char *out, int outlen, const char *src, char *dst)
{
    char *p = in;
    unsigned int  len = outlen - 1;
    if((NULL == src) || (NULL == dst) || (NULL == in) || (NULL == out))
    {
        return NULL;
    }
    if((strcmp(in, "") == 0) || (strcmp(src, "") == 0))
    {
        return NULL;
    }
    if(outlen <= 0)
    {
        return NULL;
    }
 
    while((*p != '\0') && (len > 0))
    {
        if((strncmp(p, src, strlen(src)) == 0) && !((*(p-1)<='z') && (*(p-1)>='a')) && !((*(p-1)<='Z') && (*(p-1)>='A')) && (*(p-1)!='_')  && (*(p-1)!='\\') 
		    && (*(p-1)!='%') && !((*(p+strlen(src))<='z') && (*(p+strlen(src))>='a')) && !((*(p+strlen(src))<='Z') && (*(p+strlen(src))>='A')) && (*(p+strlen(src))!='_') 
			  && !((*(p+strlen(src))<='9') && (*(p+strlen(src))>='0')))
        {
            strncat(out, dst, outlen);
            p += strlen(src);
            len -= strlen(dst);
        }
		   else
        {
            int n = strlen(out);
 
            out[n] = *p;
            out[n + 1] = '\0';
 
            p++;
            len--;
        }

    }
 
    return out;
}

/*Get two tables:var[][] and func[][].*/
int get_var_func_table(char *tokendump)
{
  FILE *fp;
  char *line= (char *)malloc(256);
  line[0]=0;
  char word1[11]="identifier",word2[8]="l_paren";
  int con1=0,con2=0,con3=0;
  fp = fopen(tokendump,"r");
  if(fp == NULL)
    {
      printf("open file error!Tokendump:%s\n",tokendump);
      exit(1);
    } 
  fgets(line,256,fp);
  while(!feof(fp))
  {
      con1=strncmp(line,word1,10);
      if(!con1)
      {
        int i=0,j=0,k=0;
        char buf[256]={0};
        for(i=10+1;j<2;i++)
        {
          if(line[i]=='\'')
            j++;
          else if(line[i]!=' ')
          {   
            buf[k]=line[i];
            k++;
          }
        }
        fgets(line,256,fp);
        if(!feof(fp))
        {
          con2=strncmp(line,word2,7);
          con3=strncmp(line,word1,10);
          if(!con2)
          {
            for(i=0;i<func_c;i++)
            {
              if(!strcmp(buf,func[i]))
                 break;
            }
            if(i==func_c)
            {
              strcpy(func[func_c],buf);
              func_c++;
            }
            fgets(line,256,fp);
          }
          else
          {
            for(i=0;i<var_c;i++)
            {
              if(!strcmp(buf,var[i]))
                 break;
            }
            if(i==var_c)
            {
              strcpy(var[var_c],buf);
              var_c++;
            }
            if(con3)
              fgets(line,256,fp);
          }
        }
       }
       else
         fgets(line,256,fp);
  } 
  free(line);
  fclose(fp);
/*  printf("The table of variables:\n");
  int x=0,y=0;
  for(x=0;x<var_c;x++)
  {
    printf("%d:%s\n",x,var[x]);
  }
  printf("The table of functions:\n");
  for(y=0;y<func_c;y++)
  {
    printf("%d:%s\n",y,func[y]);
  }*/
  return 0;
}

/*Replace all identifiers with var1,var2...and func1,func2...*/
int tokenize(char *sourcecode,char *dstcode)
{
  FILE *fp1,*fp2;
  fp1 = fopen(sourcecode,"r");
  fp2 = fopen(dstcode,"w+");
  if(fp1 == NULL)
    {
      printf("open file error!Sourcecode:%s\n",sourcecode);
      exit(1);
    } 
  if(fp2 == NULL)
    {
      printf("open file error!Dstcode:%s\n",dstcode);
      exit(1);
    } 
  char *line= (char *)malloc(256);
  line[0]=0;
  char *replace_buf0= (char *)malloc(256);
  char *replace_buf1= (char *)malloc(256);
  char *dst=(char *)malloc(16);
  if(!dst || !replace_buf0 || !replace_buf1)
  {
    printf("Memory allocation error!\n");
    exit(1);
  }
  while(!feof(fp1))
  {
    fgets(line,256,fp1);
    int i;
    for(i=0;i<var_c;i++)
    {
      dst[0]=0;
      replace_buf0[0]=0;
      snprintf(dst,12,"var%d",i);
      str_replace(line,replace_buf0,256,var[i],dst);
      strcpy(line,replace_buf0);
    }
    for(i=0;i<func_c;i++)
    {
      dst[0]=0;
      replace_buf1[0]=0;
      snprintf(dst,12,"func%d",i);
      str_replace(replace_buf0,replace_buf1,256,func[i],dst);
      strcpy(replace_buf0,replace_buf1);
    }
    fputs(replace_buf1,fp2);
  }
  free(line);
  free(dst);
  free(replace_buf0);
  free(replace_buf1);
  fclose(fp1);
  fclose(fp2);
}

int main(int argc, char *argv[])
{
/*  char path[256]={0};
  printf("Input the path of token-dump produced by clang:\n");
  scanf("%s",path);*/
  get_var_func_table(argv[1]);
/*  char path1[256]={0},path2[256]={0};
  printf("The path of sourcecode to tokenize:\n");
  scanf("%s",path1);*/
/*  printf("The path of dstcode to save:\n");
  scanf("%s",path2);*/
  tokenize(argv[2],argv[3]);
  return 0;
}
