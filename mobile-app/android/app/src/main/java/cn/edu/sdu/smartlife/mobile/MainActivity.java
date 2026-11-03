package cn.edu.sdu.smartlife.mobile;

import com.getcapacitor.BridgeActivity;
import android.os.Bundle;

public class MainActivity extends BridgeActivity {
    @Override public void onCreate(Bundle savedInstanceState) {
        registerPlugin(CampusStreamPlugin.class);
        super.onCreate(savedInstanceState);
        getBridge().getWebView().setWebViewClient(new CampusImageClient(getBridge()));
    }
}
