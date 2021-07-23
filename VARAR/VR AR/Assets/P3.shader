Shader "Unlit/P3"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _CoEfficient1("c1", float) = 2
        _CoEfficient2("c2", float) = 2
        _CoEfficient3("c3", float) = -0.01
        _CoEfficient4("c4", float) = -0.01
        _All("all", int) = 0
        _Amount("amount", float) = 0.01
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            // make fog work
            #pragma multi_compile_fog

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                UNITY_FOG_COORDS(1)
                float4 vertex : SV_POSITION;
            };

            sampler2D _MainTex;
            float4 _MainTex_ST;
            float _CoEfficient1;
            float _CoEfficient2;
            float _CoEfficient3;
            float _CoEfficient4;
            int _All;
            float _Amount;

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                float theta = atan2(o.vertex.x, o.vertex.y);
                float r = sqrt(o.vertex.x*o.vertex.x + o.vertex.y*o.vertex.y);
                r *= 1.0 + _CoEfficient1 * (r * r) + _CoEfficient2 * (r * r * r * r);
                
                o.vertex.x = r * sin(theta);
                o.vertex.y = r * cos(theta);


                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                // sample the texture


                if (_All == 1) {
                    float theta;
                
                
                i.uv -= 0.5;
                theta = atan2(i.uv.x, i.uv.y);
                
                i.uv += 0.5;

                
                //in terms of middle:


                i.uv -= 0.5;
                float r = sqrt(i.uv.x*i.uv.x + i.uv.y*i.uv.y);
                r *= _CoEfficient3 + _CoEfficient4 * (r * r);

                i.uv.x = 0.5 + r * sin(theta);
                i.uv.y =  0.5 + r * cos(theta);

                float2 R = float2(0.5 + (r - _Amount) * sin(theta), 0.5 + (r - _Amount) * cos(theta));
                float2 G = float2(0.5 + (r) * sin(theta), 0.5 + (r) * cos(theta));
                float2 B = float2(0.5 + (r + _Amount) * sin(theta), 0.5 + (r + _Amount) * cos(theta));

                fixed4 colR = tex2D(_MainTex, R);
                fixed4 colG = tex2D(_MainTex, G);
                fixed4 colB = tex2D(_MainTex, B);

                fixed4 col = tex2D(_MainTex, i.uv);
                col.r = colR.r;
                col.b = colB.b;
                col.g = colG.g;
                return col;
               

                }






                fixed4 col2 = tex2D(_MainTex, i.uv);
                // apply fog
                
                return col2;
            }
            ENDCG
        }
    }
}
