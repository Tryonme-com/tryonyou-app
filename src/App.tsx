import React, { useState } from 'react';
import { Layout, Button, Input, Card, Row, Col, Typography, Space, notification } from 'antd';
import { ArrowRightOutlined, MirrorOutlined, CheckCircleOutlined, UserOutlined } from '@ant-design/icons';

const { Header, Content } = Layout;
const { Title, Paragraph, Text } = Typography;

// 🔥 CONFIGURACIÓN DE CONVERSIÓN EXTREMA 🔥
const CONFIG = {
    HEADLINE: "Sabrás si te queda bien, antes de comprarlo.", // Dolor Directo
    SUBHEADLINE: "Sube tu foto, pruébatela en segundos y dile adiós a las devoluciones.",
    CTA_TEXT: "Pruébatela YA (5 slots de prueba hoy)", // Urgencia y Escasez (FOMO)
    // 🔥 Reemplaza con tu URL real de Webhook de Make leads 🔥
    MAKE_WEBHOOK: "https://hook.us1.make.com/tu_id_unico_leads",
    PROMISE: "Validado por el Protocolo 7.500€ de BPI",
    DEMO_GIF: "/public/mirror-sanctuary-demo.gif" // Asegúrate de que este archivo existe
};

const App: React.FC = () => {
    const [email, setEmail] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    const handleJoinWaitlist = async () => {
        if (!email || !email.includes('@')) {
            notification.error({ message: '⚠️ Email no válido', description: 'Por favor, introduce un email correcto.' });
            return;
        }
        setLoading(true);
        try {
            const response = await fetch(CONFIG.MAKE_WEBHOOK, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email.toLowerCase(), timestamp: new Date().toISOString() }),
            });

            if (response.ok) {
                notification.success({ 
                    message: '🚀 ¡Dentro!', 
                    description: 'Estás en la waitlist. ¡FOMO activo!',
                    icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />
                });
                setEmail('');
            } else {
                notification.warning({ message: '⚠️ Error', description: 'No se pudo guardar el lead.' });
            }
        } catch (error) {
            notification.error({ message: '❌ Error Crítico', description: 'Revisa la conexión.' });
        }
        setLoading(false);
    };

    return (
        <Layout className="layout" style={{ background: '#f0f2f5', minHeight: '100vh' }}>
            <Header style={{ background: '#001529', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 50px' }}>
                <Title level={3} style={{ color: 'white', margin: 0 }}>TryOnYou.app</Title>
                <Button type="primary" ghost icon={<MirrorOutlined />}>BETA PRIVADA</Button>
            </Header>

            <Content style={{ padding: '80px 50px' }}>
                <Row gutter={[48, 48]} align="middle" style={{ maxWidth: '1200px', margin: '0 auto' }}>
                    {/* HERO SECTION */}
                    <Col xs={24} md={12}>
                        <Space direction="vertical" size="large">
                            <Title level={1} style={{ fontSize: '48px', fontWeight: 800, color: '#001529', lineHeight: 1.1 }}>
                                {CONFIG.HEADLINE}
                            </Title>
                            <Paragraph style={{ fontSize: '18px', color: '#595959' }}>
                                {CONFIG.SUBHEADLINE}
                            </Paragraph>
                            
                            {/* CAPTURA DE LEADS */}
                            <Card style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                                <Row gutter={16}>
                                    <Col flex="auto">
                                        <Input 
                                            size="large" 
                                            prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
                                            placeholder="Tu email (ej. inditex@fashion.com)" 
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            style={{ borderRadius: '8px', height: '50px' }}
                                        />
                                    </Col>
                                    <Col>
                                        <Button 
                                            type="primary" 
                                            size="large" 
                                            icon={<ArrowRightOutlined />} 
                                            onClick={handleJoinWaitlist}
                                            loading={loading}
                                            style={{ borderRadius: '8px', height: '50px', background: '#1890ff' }}
                                        >
                                            {CONFIG.CTA_TEXT}
                                        </Button>
                                    </Col>
                                </Row>
                                <Paragraph style={{ margin: '12px 0 0 0', textAlign: 'center' }}>
                                    <CheckCircleOutlined style={{ color: '#52c41a' }} /> 
                                    <Text type="secondary" style={{ marginLeft: '8px' }}>
                                        {CONFIG.PROMISE}
                                    </Text>
                                </Paragraph>
                            </Card>
                        </Space>
                    </Col>

                    {/* DEMO GIF */}
                    <Col xs={24} md={12}>
                        <Card cover={<img alt="Demo" src={CONFIG.DEMO_GIF} />} style={{ borderRadius: '12px', border: '2px solid #1890ff', overflow:'hidden' }} />
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
};

export default App;
