Shader "UI/RoundedGradient"
{
    Properties
    {
        _TopColor    ("Top Color", Color)    = (0.0078, 0.2118, 0.6510, 1)   // #0236A6
        _BottomColor ("Bottom Color", Color) = (0.3412, 0.6784, 1.0000, 1)   // #57ADFF
        _RadiusN     ("Corner Radius (0-0.5)", Range(0,0.5)) = 0.12
        _SoftnessN   ("Edge Softness (0-0.1)", Range(0,0.1)) = 0.008
        _Color       ("Tint", Color) = (1,1,1,1) // standard UI tint
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent"
            "IgnoreProjector"="True"
            "RenderType"="Transparent"
            "CanUseSpriteAtlas"="True"
        }

        Stencil
        {
            Ref [_Stencil]
            Comp [_StencilComp]
            Pass [_StencilOp]
            ReadMask [_StencilReadMask]
            WriteMask [_StencilWriteMask]
        }

        Cull Off
        ZWrite Off
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            #include "UnityUI.cginc"

            struct appdata_t
            {
                float4 vertex : POSITION;
                float2 uv     : TEXCOORD0;
                float4 color  : COLOR;
            };

            struct v2f
            {
                float4 pos      : SV_POSITION;
                float2 uv       : TEXCOORD0;
                float4 color    : COLOR;
                float4 worldPos : TEXCOORD1;
            };

            float4 _ClipRect;
            float4 _TopColor, _BottomColor, _Color;
            float  _RadiusN, _SoftnessN;

            v2f vert(appdata_t v)
            {
                v2f o;
                o.pos      = UnityObjectToClipPos(v.vertex);
                o.uv       = v.uv;              // 0..1 across rect
                o.color    = v.color * _Color;  // UI vertex tint
                o.worldPos = v.vertex;
                return o;
            }

            // Signed distance to rounded rect in UV space (-1..1)
            float sdRoundRect(float2 p, float rN)
            {
                // p in -1..1; rN is 0..0.5 of the smaller dimension
                float r = saturate(rN) * 1.0;           // convert to -1..1 space
                float2 q = abs(p) - (1.0 - 2.0*r);
                return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                // vertical gradient (0 bottom -> 1 top)
                float t = saturate(i.uv.y);
                float4 grad = lerp(_BottomColor, _TopColor, t);

                // build rounded-rect alpha
                float2 p = i.uv * 2.0 - 1.0; // -1..1
                float d  = sdRoundRect(p, _RadiusN);
                float edge = saturate(0.5 - d / max(_SoftnessN, 1e-4)); // AA edge

                // UI masking/clipping support (RectMask2D, Mask)
                float mask = UnityGet2DClipping(i.worldPos, _ClipRect);

                float4 col = grad * i.color;
                col.a *= edge * mask;

                return col;
            }
            ENDCG
        }
    }
    FallBack Off
}
