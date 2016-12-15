# Notes on Logback

Logback is the default in SpringBoot

http://logback.qos.ch/manual/introduction.html

Its made up of 3 modules.  Core, Classic and Access.  Access is a web UI layer.

## Basics of Using

Classic gives you standard SLF4J API making it standard with other popular logging.

    import org.slf4j.Logger;
    import org.slf4j.LoggerFactory;

    public class ClusteratorAppTests {
        Logger logger = LoggerFactory.getLogger(this.getClass());
        public void testMapStringObject()  {
            logger.error("bob");
            logger.warn("bob");
            logger.info("bob");
            logger.debug("bob");
            logger.trace("bob");
        }
    }

You can also get back the loggerContext to see whats going on.

        LoggerContext lc = (ch.qos.logback.classic.LoggerContext) LoggerFactory.getILoggerFactory();
        StatusPrinter.print(lc);

And you can get the underlying logback logger and be able to do things like set logging level etc.

        ch.qos.logback.classic.Logger logger =
                (ch.qos.logback.classic.Logger) LoggerFactory.getLogger("com.foo");
        //set its Level to INFO. The setLevel() method requires a logback logger
        logger.setLevel(Level. INFO);

If you get a classic logger back with a specific name.. It is the SAME logger as any other. There
is only one "com.foo" logger.  that can be handy to know.

## Don't build your logged strings, use the logger formating options.

Building strings on log output that might not be used is inefficent. It can be significant if you have a lot of
debug out put that is not printed out.

From: http://logback.qos.ch/manual/architecture.html

The following two lines will yield the exact same output. However, in case of a disabled logging statement, the second variant will outperform the first variant by a factor of at least 30.

    logger.debug("The new entry is "+entry+".");
    logger.debug("The new entry is {}.", entry);

A two argument variant is also available. For example, you can write:

    logger.debug("The new entry is {}. It replaces {}.", entry, oldEntry);

If three or more arguments need to be passed, an Object[] variant is also available. For example, you can write:

    Object[] paramArray = {newVal, below, above};
    logger.debug("Value {} was inserted between {} and {}.", paramArray);

# Configuration

http://logback.qos.ch/manual/configuration.html

Here are a few cool things:

    <configuration debug="true">
        <!-- You can change log levels via JMX ie. type jconsole with this app up. -->
        <jmxConfigurator />
        <!-- Properties can also be set from property files and from JNDI -->
        <property name="NAME" value="Clusterator" />
        <!-- Context may be extremely important at an agregator node such as ELK -->
        <contextName>${NAME}</contextName>

        <!-- You'll also want to look at RollingFileAppender -->
        <appender name="FILE" class="ch.qos.logback.core.FileAppender">
            <file>${NAME}.log</file>

            <encoder>
                <pattern>%date %level %contextName [%thread] %logger{10} [%file:%line] %msg%n</pattern>
            </encoder>
        </appender>
        <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
            <!-- encoders are  by default assigned the type
                 ch.qos.logback.classic.encoder.PatternLayoutEncoder -->
            <encoder>
                <pattern>%-5level %logger{36} - %msg%n</pattern>
            </encoder>
        </appender>
        <!-- Logging at the DEBUG level only for this path and its childrenn -->
        <logger name="com.svds.push.ClusteratorAppTests" level="DEBUG"/>
        <root level="INFO">
            <appender-ref ref="FILE" />
            <appender-ref ref="STDOUT" />
        </root>
    </configuration>
