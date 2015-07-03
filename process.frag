// center position of cone
uniform float PointerX;
uniform float PointerY;
// radius
uniform float PointerRadius;

uniform sampler2D TextureUnit1;

void main (void)
{
	// get texture color at that fragment
	vec4 first = texture2D( TextureUnit1, gl_TexCoord[0].st);
	// get coordinates on the screen of the fragment and calculate distance
	//gl_FragCoord.x, gl_FragCoord.y
	//float distance = sqrt(pow(gl_FragCoord.x-PointerX,2.0)+pow(gl_FragCoord.y-PointerY,2.0));
	//if(distance > PointerRadius)
	//	gl_FragColor = vec4(0.0,0.0,0.0,1.0);
	//else
		gl_FragColor = first * vec4(1.0,1.0,1.0,0.0);
	
}