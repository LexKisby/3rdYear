Shader "Unlit/P1F"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _CoEfficient1("c1", float) = 2
        _CoEfficient2("c2", float) = -2
        _CoEfficient3("c3", float) = 10
        _CoEfficient4("c4", float) = 10
       _Forward("Forward", int) = 1
       _Inverse("Inverse", int) = 0
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
            int _Forward;
            int _Inverse;

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                UNITY_TRANSFER_FOG(o,o.vertex);
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                // sample the texture
                //fixed4 col = tex2D(_MainTex, i.uv);
                float theta;
                
                
                i.uv -= 0.5;
                theta = atan2(i.uv.x, i.uv.y);
                
                i.uv += 0.5;

                if (_Forward == 1) {
                //in terms of middle:


                i.uv -= 0.5;
                float r = sqrt(i.uv.x*i.uv.x + i.uv.y*i.uv.y);
                r *= 1.0 + _CoEfficient1 * (r * r) + _CoEfficient2 * (r * r * r * r);

                i.uv.x = 0.5 + r * sin(theta);
                i.uv.y =  0.5 + r * cos(theta);
                }

                if (_Inverse == 1) {
                    i.uv -= 0.5;
                    float r = sqrt(i.uv.x*i.uv.x + i.uv.y*i.uv.y);
                    float r2 = r * r;
                    float r4 = r2 * r2;
                    float r8 = r4 * r4;
                    float r6 = r4 * r2;
                    float ru = _CoEfficient3*r2 + _CoEfficient4*r4 + _CoEfficient3*_CoEfficient3*r4 + _CoEfficient4*_CoEfficient4*r8 + 2*_CoEfficient3*_CoEfficient4*r6;
                    ru /= (1 + 4*_CoEfficient3*r2 + 6*_CoEfficient4*r4);
                    
                    i.uv.x = 0.5 + ru * sin(theta);
                    i.uv.y =  0.5 + ru * cos(theta);
                }

                fixed4 col = tex2D(_MainTex, i.uv);
                
                return col;
                
            }
            ENDCG
        }
    }
}